"""
Dashboard Views - Das Cockpit für Peter Zwegats Buchhaltungsbutler!
"""

from datetime import timedelta
from decimal import Decimal

from django.db.models import Count, Sum
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, render
from django.utils import timezone

from belege.models import Beleg
from buchungen.models import Buchungssatz, Geschaeftspartner
from konten.models import Konto


def dashboard_view(request):
    """
    Hauptdashboard mit allen wichtigen Kennzahlen.
    Peter Zwegat: "Überblick verschaffen ist der erste Schritt zum Erfolg!"
    """
    heute = timezone.now().date()
    monat_start = heute.replace(day=1)
    jahr_start = heute.replace(month=1, day=1)

    # Zeiträume für Vergleiche
    letzter_monat = (monat_start - timedelta(days=1)).replace(day=1)
    letztes_jahr = jahr_start.replace(year=jahr_start.year - 1)

    # Einnahmen und Ausgaben aktueller Monat
    einnahmen_monat = Buchungssatz.objects.filter(
        buchungsdatum__gte=monat_start,
        haben_konto__nummer__startswith='8'  # Ertragskonten
    ).aggregate(
        summe=Sum('betrag')
    )['summe'] or Decimal('0')

    ausgaben_monat = Buchungssatz.objects.filter(
        buchungsdatum__gte=monat_start,
        soll_konto__nummer__startswith='4'  # Aufwandskonten
    ).aggregate(
        summe=Sum('betrag')
    )['summe'] or Decimal('0')

    gewinn_monat = einnahmen_monat - ausgaben_monat

    # Einnahmen und Ausgaben aktuelles Jahr
    einnahmen_jahr = Buchungssatz.objects.filter(
        buchungsdatum__gte=jahr_start,
        haben_konto__nummer__startswith='8'
    ).aggregate(
        summe=Sum('betrag')
    )['summe'] or Decimal('0')

    ausgaben_jahr = Buchungssatz.objects.filter(
        buchungsdatum__gte=jahr_start,
        soll_konto__nummer__startswith='4'
    ).aggregate(
        summe=Sum('betrag')
    )['summe'] or Decimal('0')

    gewinn_jahr = einnahmen_jahr - ausgaben_jahr

    # Vergleich mit Vormonat
    einnahmen_vormonat = Buchungssatz.objects.filter(
        buchungsdatum__gte=letzter_monat,
        buchungsdatum__lt=monat_start,
        haben_konto__nummer__startswith='8'
    ).aggregate(
        summe=Sum('betrag')
    )['summe'] or Decimal('0')

    # Trend berechnen
    einnahmen_trend = 0
    if einnahmen_vormonat > 0:
        einnahmen_trend = float((einnahmen_monat - einnahmen_vormonat) / einnahmen_vormonat * 100)

    # Statistiken
    stats = {
        'buchungen_gesamt': Buchungssatz.objects.count(),
        'buchungen_monat': Buchungssatz.objects.filter(
            buchungsdatum__gte=monat_start
        ).count(),
        'belege_unbearbeitet': Beleg.objects.filter(
            status__in=['NEU', 'FEHLER']
        ).count(),
        'geschaeftspartner_aktiv': Geschaeftspartner.objects.filter(
            aktiv=True
        ).count(),
    }

    # Letzte Buchungen
    letzte_buchungen = Buchungssatz.objects.select_related(
        'soll_konto', 'haben_konto', 'geschaeftspartner', 'beleg'
    ).order_by('-erstellt_am')[:10]

    # Offene Belege
    offene_belege = Beleg.objects.filter(
        status__in=['NEU', 'GEPRUEFT']
    ).select_related('geschaeftspartner').order_by('-rechnungsdatum')[:5]

    # Top Ausgaben-Kategorien (letzten 30 Tage)
    vor_30_tagen = heute - timedelta(days=30)
    top_ausgaben = Buchungssatz.objects.filter(
        buchungsdatum__gte=vor_30_tagen,
        soll_konto__nummer__startswith='4'
    ).values(
        'soll_konto__name'
    ).annotate(
        summe=Sum('betrag'),
        anzahl=Count('id')
    ).order_by('-summe')[:5]

    # Monats-Chart-Daten (letzten 12 Monate)
    chart_data = []
    for i in range(12):
        chart_monat = (heute.replace(day=1) - timedelta(days=30*i)).replace(day=1)
        chart_monat_ende = (chart_monat.replace(day=28) + timedelta(days=4)).replace(day=1) - timedelta(days=1)

        einnahmen = Buchungssatz.objects.filter(
            buchungsdatum__gte=chart_monat,
            buchungsdatum__lte=chart_monat_ende,
            haben_konto__nummer__startswith='8'
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0')

        ausgaben = Buchungssatz.objects.filter(
            buchungsdatum__gte=chart_monat,
            buchungsdatum__lte=chart_monat_ende,
            soll_konto__nummer__startswith='4'
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0')

        chart_data.insert(0, {
            'monat': chart_monat.strftime('%b %Y'),
            'einnahmen': float(einnahmen),
            'ausgaben': float(ausgaben),
            'gewinn': float(einnahmen - ausgaben)
        })

    # Peter Zwegat Motivations-Sprüche
    zwegat_sprueche = [
        "Ihre Bücher sind in Ordnung - das freut mich!",
        "Weiter so! Ordnung ist das halbe Leben.",
        "Jeder Euro zählt - und Sie zählen jeden Euro!",
        "Buchhaltung kann Spaß machen - sehen Sie selbst!",
        "Ihre Finanzen sind auf dem richtigen Weg!",
        "Peter Zwegat wäre stolz auf diese Ordnung!",
        "Kontrolle ist besser als Nachsicht - gut gemacht!",
        "Ihre Disziplin zahlt sich aus!"
    ]

    import random
    zwegat_spruch = random.choice(zwegat_sprueche)

    context = {
        'page_title': 'Dashboard',
        'page_subtitle': f'Willkommen zurück! Heute ist {heute.strftime("%A, %d. %B %Y")}',

        # Finanzkennzahlen
        'einnahmen_monat': einnahmen_monat,
        'ausgaben_monat': ausgaben_monat,
        'gewinn_monat': gewinn_monat,
        'einnahmen_jahr': einnahmen_jahr,
        'ausgaben_jahr': ausgaben_jahr,
        'gewinn_jahr': gewinn_jahr,
        'einnahmen_trend': einnahmen_trend,

        # Statistiken
        'stats': stats,

        # Listen
        'letzte_buchungen': letzte_buchungen,
        'offene_belege': offene_belege,
        'top_ausgaben': top_ausgaben,

        # Chart-Daten
        'chart_data': chart_data,

        # Peter Zwegat
        'zwegat_spruch': zwegat_spruch,

        # Zeiträume
        'aktueller_monat': heute.strftime('%B %Y'),
        'aktuelles_jahr': heute.year,
    }

    return render(request, 'dashboard/index.html', context)


def kennzahlen_ajax(request):
    """
    AJAX-Endpoint für Live-Kennzahlen.
    """
    heute = timezone.now().date()
    monat_start = heute.replace(day=1)

    # Aktuelle Zahlen
    einnahmen_heute = Buchungssatz.objects.filter(
        buchungsdatum=heute,
        haben_konto__nummer__startswith='8'
    ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0')

    buchungen_heute = Buchungssatz.objects.filter(
        buchungsdatum=heute
    ).count()

    return JsonResponse({
        'einnahmen_heute': float(einnahmen_heute),
        'buchungen_heute': buchungen_heute,
        'timestamp': timezone.now().isoformat(),
    })


def eur_view(request):
    """
    Einnahmen-Überschuss-Rechnung (EÜR) für das Finanzamt.
    Peter Zwegat: "Das ist das Wichtigste - hier sieht das Finanzamt alles!"
    """
    jahr = int(request.GET.get('jahr', timezone.now().year))
    jahr_start = timezone.now().date().replace(year=jahr, month=1, day=1)
    jahr_ende = timezone.now().date().replace(year=jahr, month=12, day=31)

    # Einnahmen nach Kategorien
    einnahmen_kategorien = {
        'erlöse': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            haben_konto__nummer__startswith='8'
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'sonstige_einnahmen': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            haben_konto__nummer__startswith='48'  # Sonstige betriebliche Erträge
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),
    }

    # Ausgaben nach Kategorien
    ausgaben_kategorien = {
        'wareneinsatz': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['5000', '5100', '5200']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'personalkosten': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__startswith='62'
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'mieten': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4120', '4130']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'buerokosten': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4980', '4985', '4990']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'marketing': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4600', '4610', '4620']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'reisekosten': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4650', '4655']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'kfz_kosten': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4520', '4530']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'versicherungen': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__in=['4360', '4370']
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),

        'sonstige_ausgaben': Buchungssatz.objects.filter(
            buchungsdatum__gte=jahr_start,
            buchungsdatum__lte=jahr_ende,
            soll_konto__nummer__startswith='4',
            soll_konto__nummer__regex=r'^4[0-3]'  # Sonstige Aufwendungen
        ).exclude(
            soll_konto__nummer__in=[
                '4120', '4130', '4360', '4370', '4520', '4530',
                '4600', '4610', '4620', '4650', '4655', '4980', '4985', '4990'
            ]
        ).aggregate(summe=Sum('betrag'))['summe'] or Decimal('0'),
    }

    # Summen berechnen
    gesamte_einnahmen = sum(einnahmen_kategorien.values())
    gesamte_ausgaben = sum(ausgaben_kategorien.values())
    eur_ergebnis = gesamte_einnahmen - gesamte_ausgaben

    # Verfügbare Jahre für Dropdown
    erste_buchung = Buchungssatz.objects.order_by('buchungsdatum').first()
    if erste_buchung:
        start_jahr = erste_buchung.buchungsdatum.year
    else:
        start_jahr = timezone.now().year

    verfuegbare_jahre = list(range(start_jahr, timezone.now().year + 1))

    context = {
        'page_title': f'EÜR {jahr}',
        'page_subtitle': 'Einnahmen-Überschuss-Rechnung für das Finanzamt',
        'jahr': jahr,
        'verfuegbare_jahre': verfuegbare_jahre,

        # EÜR-Daten
        'einnahmen_kategorien': einnahmen_kategorien,
        'ausgaben_kategorien': ausgaben_kategorien,
        'gesamte_einnahmen': gesamte_einnahmen,
        'gesamte_ausgaben': gesamte_ausgaben,
        'eur_ergebnis': eur_ergebnis,

        # Zeitraum
        'jahr_start': jahr_start,
        'jahr_ende': jahr_ende,
    }

    return render(request, 'auswertungen/eur.html', context)


def kontenblatt_view(request, konto_id):
    """
    Detailliertes Kontenblatt für ein einzelnes Konto.
    Peter Zwegat: "Hier sehen Sie jeden Euro - bis auf den Cent genau!"
    """
    konto = get_object_or_404(Konto, id=konto_id)

    # Zeitraum
    jahr = int(request.GET.get('jahr', timezone.now().year))
    monat = request.GET.get('monat')

    jahr_start = timezone.now().date().replace(year=jahr, month=1, day=1)
    jahr_ende = timezone.now().date().replace(year=jahr, month=12, day=31)

    # Filter nach Monat wenn gewählt
    if monat:
        monat = int(monat)
        jahr_start = jahr_start.replace(month=monat)
        if monat == 12:
            jahr_ende = jahr_start.replace(day=31)
        else:
            jahr_ende = jahr_start.replace(month=monat+1, day=1) - timedelta(days=1)

    # Buchungen für dieses Konto
    soll_buchungen = Buchungssatz.objects.filter(
        soll_konto=konto,
        buchungsdatum__gte=jahr_start,
        buchungsdatum__lte=jahr_ende
    ).select_related('haben_konto', 'geschaeftspartner', 'beleg').order_by('buchungsdatum')

    haben_buchungen = Buchungssatz.objects.filter(
        haben_konto=konto,
        buchungsdatum__gte=jahr_start,
        buchungsdatum__lte=jahr_ende
    ).select_related('soll_konto', 'geschaeftspartner', 'beleg').order_by('buchungsdatum')

    # Salden berechnen
    soll_summe = soll_buchungen.aggregate(summe=Sum('betrag'))['summe'] or Decimal('0')
    haben_summe = haben_buchungen.aggregate(summe=Sum('betrag'))['summe'] or Decimal('0')

    # Saldo je nach Kontotyp
    if konto.nummer.startswith(('0', '1', '4', '5', '6')):  # Aktiv- und Aufwandskonten
        saldo = soll_summe - haben_summe
    else:  # Passiv- und Ertragskonten
        saldo = haben_summe - soll_summe

    context = {
        'page_title': f'Kontenblatt {konto.nummer}',
        'page_subtitle': konto.name,
        'konto': konto,
        'jahr': jahr,
        'monat': monat,
        'jahr_start': jahr_start,
        'jahr_ende': jahr_ende,

        'soll_buchungen': soll_buchungen,
        'haben_buchungen': haben_buchungen,
        'soll_summe': soll_summe,
        'haben_summe': haben_summe,
        'saldo': saldo,

        'verfuegbare_jahre': list(range(2020, timezone.now().year + 1)),
        'verfuegbare_monate': [
            (1, 'Januar'), (2, 'Februar'), (3, 'März'), (4, 'April'),
            (5, 'Mai'), (6, 'Juni'), (7, 'Juli'), (8, 'August'),
            (9, 'September'), (10, 'Oktober'), (11, 'November'), (12, 'Dezember')
        ],
    }

    return render(request, 'auswertungen/kontenblatt.html', context)
