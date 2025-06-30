"""
WebAuthn/FIDO2 Views für passwortlose Authentifizierung.

Implementiert Registration und Authentication mit FIDO2-Keys.
"""

import base64
import json
from datetime import timedelta

from django.conf import settings
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from webauthn import (
    generate_authentication_options,
    generate_registration_options,
    verify_authentication_response,
    verify_registration_response,
)
from webauthn.helpers.structs import (
    AuthenticationCredential,
    AuthenticatorSelectionCriteria,
    RegistrationCredential,
    UserVerificationRequirement,
)

from .models import WebAuthnChallenge, WebAuthnCredential

# WebAuthn-Konfiguration
RP_ID = getattr(settings, "WEBAUTHN_RP_ID", "localhost")
RP_NAME = getattr(settings, "WEBAUTHN_RP_NAME", "llkjj_art")
ORIGIN = getattr(settings, "WEBAUTHN_ORIGIN", "http://localhost:8000")


def webauthn_setup_view(request):
    """
    Zeigt die WebAuthn-Setup-Seite für FIDO2-Schlüssel-Registrierung.
    """
    if not request.user.is_authenticated:
        return redirect("authentifizierung:anmelden")

    # Vorhandene FIDO2-Schlüssel des Benutzers
    credentials = WebAuthnCredential.objects.filter(user=request.user, is_active=True)

    context = {
        "credentials": credentials,
        "has_credentials": credentials.exists(),
    }

    return render(request, "authentifizierung/webauthn_setup.html", context)


@require_POST
@csrf_exempt
def webauthn_register_begin(request):
    """
    Startet WebAuthn-Registrierung - erzeugt Challenge.
    """
    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Benutzername erforderlich"}, status=400)

        # Benutzer finden oder erstellen
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Benutzer nicht gefunden"}, status=404)

        # Vorhandene Credentials für Ausschluss
        existing_credentials = WebAuthnCredential.objects.filter(
            user=user, is_active=True
        )

        exclude_credentials = [
            {"id": cred.credential_id_bytes, "type": "public-key"}
            for cred in existing_credentials
        ]

        # Registrierungs-Optionen generieren
        options = generate_registration_options(
            rp_id=RP_ID,
            rp_name=RP_NAME,
            user_id=str(user.id).encode(),
            user_name=user.username,
            user_display_name=user.get_full_name() or user.username,
            exclude_credentials=exclude_credentials,
            authenticator_selection=AuthenticatorSelectionCriteria(
                user_verification=UserVerificationRequirement.PREFERRED
            ),
        )

        # Challenge speichern
        challenge_obj = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(options.challenge).decode(),
            user=user,
            challenge_type="registration",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        # Options für Frontend serialisieren
        options_json = {
            "rp": {"id": options.rp.id, "name": options.rp.name},
            "user": {
                "id": base64.b64encode(options.user.id).decode(),
                "name": options.user.name,
                "displayName": options.user.display_name,
            },
            "challenge": base64.b64encode(options.challenge).decode(),
            "pubKeyCredParams": [
                {"type": "public-key", "alg": param.alg}
                for param in options.pub_key_cred_params
            ],
            "timeout": options.timeout,
            "excludeCredentials": [
                {"id": base64.b64encode(cred["id"]).decode(), "type": cred["type"]}
                for cred in exclude_credentials
            ],
            "authenticatorSelection": {
                "userVerification": options.authenticator_selection.user_verification,
            },
            "attestation": options.attestation,
            "challengeId": str(challenge_obj.challenge_id),
        }

        return JsonResponse(options_json)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@csrf_exempt
def webauthn_register_complete(request):
    """
    Schließt WebAuthn-Registrierung ab - verifiziert Response.
    """
    try:
        data = json.loads(request.body)
        challenge_id = data.get("challengeId")
        credential_data = data.get("credential")
        device_name = data.get("deviceName", "FIDO2-Schlüssel")

        if not challenge_id or not credential_data:
            return JsonResponse({"error": "Unvollständige Daten"}, status=400)

        # Challenge finden
        try:
            challenge_obj = WebAuthnChallenge.objects.get(
                challenge_id=challenge_id, challenge_type="registration"
            )
        except WebAuthnChallenge.DoesNotExist:
            return JsonResponse({"error": "Challenge nicht gefunden"}, status=404)

        if challenge_obj.is_expired:
            challenge_obj.delete()
            return JsonResponse({"error": "Challenge abgelaufen"}, status=400)

        # Credential Response aufbauen
        credential = RegistrationCredential.parse_raw(json.dumps(credential_data))

        # Registrierung verifizieren
        verification = verify_registration_response(
            credential=credential,
            expected_challenge=challenge_obj.challenge_bytes,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
        )

        if verification.verified:
            # Credential in Datenbank speichern
            WebAuthnCredential.objects.create(
                user=challenge_obj.user,
                credential_id=base64.b64encode(verification.credential_id).decode(),
                public_key=base64.b64encode(
                    verification.credential_public_key
                ).decode(),
                sign_count=verification.sign_count,
                name=device_name,
            )

            # Challenge löschen
            challenge_obj.delete()

            return JsonResponse(
                {
                    "verified": True,
                    "message": "FIDO2-Schlüssel erfolgreich registriert!",
                }
            )
        else:
            return JsonResponse({"error": "Verifizierung fehlgeschlagen"}, status=400)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@csrf_exempt
def webauthn_auth_begin(request):
    """
    Startet WebAuthn-Authentifizierung - erzeugt Challenge.
    """
    try:
        data = json.loads(request.body)
        username = data.get("username")

        if not username:
            return JsonResponse({"error": "Benutzername erforderlich"}, status=400)

        # Benutzer finden
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return JsonResponse({"error": "Benutzer nicht gefunden"}, status=404)

        # Aktive Credentials des Benutzers
        credentials = WebAuthnCredential.objects.filter(user=user, is_active=True)

        if not credentials.exists():
            return JsonResponse(
                {"error": "Keine FIDO2-Schlüssel für diesen Benutzer gefunden"},
                status=404,
            )

        # Authentifizierungs-Optionen generieren
        allow_credentials = [
            {"id": cred.credential_id_bytes, "type": "public-key"}
            for cred in credentials
        ]

        options = generate_authentication_options(
            rp_id=RP_ID,
            allow_credentials=allow_credentials,
            user_verification=UserVerificationRequirement.PREFERRED,
        )

        # Challenge speichern
        challenge_obj = WebAuthnChallenge.objects.create(
            challenge=base64.b64encode(options.challenge).decode(),
            user=user,
            challenge_type="authentication",
            expires_at=timezone.now() + timedelta(minutes=5),
        )

        # Options für Frontend serialisieren
        options_json = {
            "challenge": base64.b64encode(options.challenge).decode(),
            "timeout": options.timeout,
            "rpId": options.rp_id,
            "allowCredentials": [
                {"id": base64.b64encode(cred["id"]).decode(), "type": cred["type"]}
                for cred in allow_credentials
            ],
            "userVerification": options.user_verification,
            "challengeId": str(challenge_obj.challenge_id),
        }

        return JsonResponse(options_json)

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@require_POST
@csrf_exempt
def webauthn_auth_complete(request):
    """
    Schließt WebAuthn-Authentifizierung ab - verifiziert Response und loggt ein.
    """
    try:
        data = json.loads(request.body)
        challenge_id = data.get("challengeId")
        credential_data = data.get("credential")

        if not challenge_id or not credential_data:
            return JsonResponse({"error": "Unvollständige Daten"}, status=400)

        # Challenge finden
        try:
            challenge_obj = WebAuthnChallenge.objects.get(
                challenge_id=challenge_id, challenge_type="authentication"
            )
        except WebAuthnChallenge.DoesNotExist:
            return JsonResponse({"error": "Challenge nicht gefunden"}, status=404)

        if challenge_obj.is_expired:
            challenge_obj.delete()
            return JsonResponse({"error": "Challenge abgelaufen"}, status=400)

        # Credential finden
        credential_id = base64.b64decode(credential_data["id"])
        try:
            stored_credential = WebAuthnCredential.objects.get(
                credential_id=base64.b64encode(credential_id).decode(),
                user=challenge_obj.user,
                is_active=True,
            )
        except WebAuthnCredential.DoesNotExist:
            return JsonResponse({"error": "Credential nicht gefunden"}, status=404)

        # Credential Response aufbauen
        credential = AuthenticationCredential.parse_raw(json.dumps(credential_data))

        # Authentifizierung verifizieren
        verification = verify_authentication_response(
            credential=credential,
            expected_challenge=challenge_obj.challenge_bytes,
            expected_origin=ORIGIN,
            expected_rp_id=RP_ID,
            credential_public_key=stored_credential.public_key_bytes,
            credential_current_sign_count=stored_credential.sign_count,
        )

        if verification.verified:
            # Sign Count aktualisieren
            stored_credential.sign_count = verification.new_sign_count
            stored_credential.last_used = timezone.now()
            stored_credential.save()

            # Benutzer einloggen
            login(request, challenge_obj.user)

            # Challenge löschen
            challenge_obj.delete()

            return JsonResponse(
                {
                    "verified": True,
                    "message": "Erfolgreich mit FIDO2-Schlüssel angemeldet!",
                    "redirect": "/",  # Nach Login weiterleiten
                }
            )
        else:
            return JsonResponse(
                {"error": "Authentifizierung fehlgeschlagen"}, status=400
            )

    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)


@login_required
@require_POST
def webauthn_credential_delete(request, credential_id):
    """
    Löscht einen FIDO2-Schlüssel des aktuellen Benutzers.
    """
    try:
        credential = WebAuthnCredential.objects.get(id=credential_id, user=request.user)
        credential.delete()

        return JsonResponse(
            {"success": True, "message": "FIDO2-Schlüssel erfolgreich entfernt!"}
        )

    except WebAuthnCredential.DoesNotExist:
        return JsonResponse({"error": "Schlüssel nicht gefunden"}, status=404)
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=500)
