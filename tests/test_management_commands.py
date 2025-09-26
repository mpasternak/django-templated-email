from io import StringIO
from unittest.mock import MagicMock, patch
from django.core.management import call_command
from django.test import TestCase, override_settings


class SendTestTemplatedEmailCommandTest(TestCase):
    def test_command_with_email_addresses(self):
        """Test sending to specific email addresses."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                'test1@example.com',
                'test2@example.com',
                stdout=out
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            self.assertEqual(
                call_args.kwargs['recipient_list'],
                ['test1@example.com', 'test2@example.com']
            )
            self.assertEqual(call_args.kwargs['template_name'], 'test_email')
            self.assertIn('message', call_args.kwargs['context'])
            self.assertIsNone(call_args.kwargs['from_email'])

            output = out.getvalue()
            self.assertIn('Test email sent to', output)
            self.assertIn('test1@example.com', output)
            self.assertIn('test2@example.com', output)

    @override_settings(MANAGERS=[('Manager', 'manager@example.com')])
    def test_command_with_managers(self):
        """Test sending to managers."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                '--managers',
                stdout=out
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            self.assertEqual(
                call_args.kwargs['recipient_list'],
                ['manager@example.com']
            )
            self.assertEqual(call_args.kwargs['template_name'], 'test_email')

            output = out.getvalue()
            self.assertIn('Test email sent to managers', output)
            self.assertIn('manager@example.com', output)

    @override_settings(ADMINS=[('Admin', 'admin@example.com')])
    def test_command_with_admins(self):
        """Test sending to admins."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                '--admins',
                stdout=out
            )

            mock_send.assert_called_once()
            call_args = mock_send.call_args
            self.assertEqual(
                call_args.kwargs['recipient_list'],
                ['admin@example.com']
            )
            self.assertEqual(call_args.kwargs['template_name'], 'test_email')

            output = out.getvalue()
            self.assertIn('Test email sent to admins', output)
            self.assertIn('admin@example.com', output)

    @override_settings(
        MANAGERS=[('Manager1', 'manager1@example.com'), ('Manager2', 'manager2@example.com')],
        ADMINS=[('Admin1', 'admin1@example.com'), ('Admin2', 'admin2@example.com')]
    )
    def test_command_with_all_recipients(self):
        """Test sending to email addresses, managers, and admins."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                'user@example.com',
                '--managers',
                '--admins',
                stdout=out
            )

            # Should be called 3 times: once for direct email, once for managers, once for admins
            self.assertEqual(mock_send.call_count, 3)

            # Check each call
            calls = mock_send.call_args_list

            # First call - direct email
            self.assertEqual(
                calls[0].kwargs['recipient_list'],
                ['user@example.com']
            )

            # Second call - managers
            self.assertEqual(
                set(calls[1].kwargs['recipient_list']),
                {'manager1@example.com', 'manager2@example.com'}
            )

            # Third call - admins
            self.assertEqual(
                set(calls[2].kwargs['recipient_list']),
                {'admin1@example.com', 'admin2@example.com'}
            )

            output = out.getvalue()
            self.assertIn('user@example.com', output)
            self.assertIn('managers', output)
            self.assertIn('admins', output)

    @override_settings(MANAGERS=[], ADMINS=[])
    def test_command_with_no_managers_or_admins(self):
        """Test warning messages when no managers or admins are configured."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                '--managers',
                '--admins',
                stdout=out
            )

            # Should not be called since no managers or admins are configured
            mock_send.assert_not_called()

            output = out.getvalue()
            self.assertIn('No managers configured', output)
            self.assertIn('No admins configured', output)

    def test_template_context(self):
        """Test that the correct context is passed to the template."""
        out = StringIO()
        with patch('templated_email.management.commands.sendtesttemplatedemail.send_templated_mail') as mock_send:
            mock_send.return_value = None

            call_command(
                'sendtesttemplatedemail',
                'test@example.com',
                stdout=out
            )

            call_args = mock_send.call_args
            context = call_args.kwargs['context']
            self.assertIn('message', context)
            self.assertEqual(
                context['message'],
                "If you're reading this, it was successful."
            )