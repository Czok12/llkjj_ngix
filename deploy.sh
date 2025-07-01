#!/bin/bash

# 🚀 Production Deployment Script for llkjj_art
# This script deploys your Django application to production

set -e  # Exit on any error

echo "🚀 Starting Production Deployment..."

# Check if Docker is running
if ! docker info > /dev/null 2>&1; then
    echo "❌ Docker is not running. Please start Docker first."
    exit 1
fi

# Check if .env file exists
if [ ! -f .env.production ]; then
    echo "❌ .env.production file not found!"
    echo "Please copy .env.production.example to .env.production and configure it."
    exit 1
fi

echo "✅ Docker is running"
echo "✅ Environment file found"

# Build and start services
echo "🔨 Building Docker images..."
docker-compose -f docker-compose.prod.yml build

echo "🏃 Starting services..."
docker-compose -f docker-compose.prod.yml up -d

# Wait for database to be ready
echo "⏳ Waiting for database to be ready..."
sleep 10

# Run migrations
echo "🗄️  Running database migrations..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py migrate

# Create superuser (if needed)
echo "👤 Creating superuser..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell << EOF
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@example.com', 'admin123')
    print('Superuser created: admin/admin123')
else:
    print('Superuser already exists')
EOF

# Collect static files
echo "📦 Collecting static files..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py collectstatic --noinput

# Warm up cache
echo "🔥 Warming up cache..."
docker-compose -f docker-compose.prod.yml exec -T web python manage.py shell << EOF
try:
    from django.core.management import call_command
    call_command('performance', 'warmup')
    print('Cache warmed up successfully')
except:
    print('Cache warmup skipped (command not found)')
EOF

echo ""
echo "🎉 Deployment completed successfully!"
echo ""
echo "📊 Service Status:"
docker-compose -f docker-compose.prod.yml ps

echo ""
echo "🌐 Your application is now available at:"
echo "   http://localhost"
echo "   Admin: http://localhost/admin"
echo ""
echo "👤 Login credentials:"
echo "   Username: admin"
echo "   Password: admin123"
echo ""
echo "📝 Useful commands:"
echo "   View logs: docker-compose -f docker-compose.prod.yml logs -f"
echo "   Stop:      docker-compose -f docker-compose.prod.yml down"
echo "   Restart:   docker-compose -f docker-compose.prod.yml restart web"
echo ""
echo "🎯 Next steps:"
echo "   1. Change the admin password"
echo "   2. Configure your domain in .env.production"
echo "   3. Set up SSL certificates"
echo "   4. Configure email settings"
