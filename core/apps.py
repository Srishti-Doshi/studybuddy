from django.apps import AppConfig
import os

class CoreConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "core"

    def ready(self):
        if os.environ.get("CREATE_SUPERUSER") == "1":
            try:
                from django.contrib.auth.models import User

                if not User.objects.filter(username="admin").exists():
                    User.objects.create_superuser(
                        username="admin",
                        email="admin@example.com",
                        password="admin123"
                    )
                    print("✅ Superuser created")
            except Exception as e:
                print("❌ Superuser creation error:", e)