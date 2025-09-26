from django.conf import settings
from django.core.management.commands.sendtestemail import (
    Command as SendTestEmailCommand,
)
from templated_email import send_templated_mail


class Command(SendTestEmailCommand):
    help = "Sends a test email to the specified email address(es) using templated email."

    def handle(self, *args, **kwargs):
        subject = "Test email from sendtesttemplatedemail management command"
        message = "If you're reading this, it was successful."

        kw = dict(
            template_name="test_email",
            context={"message": message},
            from_email=None,
        )

        # Get recipient lists from parent command
        recipients = kwargs.get("email", [])

        if recipients:
            send_templated_mail(recipient_list=recipients, **kw)
            self.stdout.write(
                self.style.SUCCESS(
                    f"Test email sent to {', '.join(recipients)}."
                )
            )

        # Send to managers if requested
        if kwargs.get("managers"):
            manager_emails = [email for name, email in settings.MANAGERS]
            if manager_emails:
                send_templated_mail(recipient_list=manager_emails, **kw)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Test email sent to managers: {', '.join(manager_emails)}."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("No managers configured in settings.")
                )

        # Send to admins if requested
        if kwargs.get("admins"):
            admin_emails = [email for name, email in settings.ADMINS]
            if admin_emails:
                send_templated_mail(recipient_list=admin_emails, **kw)
                self.stdout.write(
                    self.style.SUCCESS(
                        f"Test email sent to admins: {', '.join(admin_emails)}."
                    )
                )
            else:
                self.stdout.write(
                    self.style.WARNING("No admins configured in settings.")
                )