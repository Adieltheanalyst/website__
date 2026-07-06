"""
BUILDIT CONNECTIVE - EMAIL VIA ZOHO SMTP"""

import smtplib, os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart


ZOHO_EMAIL = os.environ.get("ZOHO_EMAIL", "communications@builditconnective.co.ke")
ZOHO_PASSWORD = os.environ.get("ZOHO_PASSWORD", "BuildIT2024.")
SITE_URL = os.environ.get("SITE_URL", "https://localhost:5000")

SITE_NAME = "BuildIT Connective"

def send_email(to_email, subject, html_body, text_body=None):
    msg=MIMEMultipart("alternative")
    msg["Subject"]= subject
    msg["From"] = f"{SITE_NAME} < {ZOHO_EMAIL}>"
    msg["To"]= to_email

    if text_body:
        msg.attach(MIMEText(text_body,"plain"))
    msg.attach(MIMEText(html_body,"html"))
    try:
        with smtplib.SMTP_SSL("smtp.zoho.com",465) as server:
            server.login(ZOHO_EMAIL,ZOHO_PASSWORD)
            server.sendmail(ZOHO_EMAIL,to_email, msg.as_string())
        print(f"[EMAIL] Sent to {to_email}")
        return True, None
    except smtplib.SMTPAuthenticationError:
        err = "Zoho auth failed - check email/password in email_utils.py"
        print(f"[Email] {err}")
        return False, err
    except Exception as e:
        print(f"[EMAIL] {e}")
        return False,str(e)
    
def send_welcome_email(name,email,temp_password):
    first_name=name.split()[0]
    login_url= f"{SITE_URL}/login"
    change_url= f"{SITE_URL}/ set-password"
    subject= f"You're in, {first_name}! Your BuildIT connective login"

    html = f"""
<!DOCTYPE html>
<html>
<head><meta charset="utf-8"/></head>
<body style="margin:0;padding:0;background:#f0f4f8;font-family:Arial,sans-serif;">
  <table width="100%" cellpadding="0" cellspacing="0" style="background:#f0f4f8;padding:40px 20px;">
    <tr><td align="center">
      <table width="600" cellpadding="0" cellspacing="0" style="max-width:600px;width:100%;">

        <tr>
          <td style="background:linear-gradient(135deg,#021526,#03346E,#305E94);border-radius:16px 16px 0 0;padding:40px;text-align:center;">
            <div style="font-size:12px;font-weight:800;letter-spacing:0.15em;text-transform:uppercase;color:#8BEEE0;margin-bottom:8px;">BuildIT Connective</div>
            <h1 style="color:#FDFDFD;font-size:30px;font-weight:900;margin:0;">You're in, {first_name}! 🎉</h1>
            <p style="color:rgba(253,253,253,0.6);margin:10px 0 0;font-size:15px;">Welcome to the community</p>
          </td>
        </tr>

        <tr>
          <td style="background:#FDFDFD;padding:40px;">
            <p style="color:#021526;font-size:15px;line-height:1.7;margin:0 0 20px;">
              Hey {first_name}, your BuildIT Connective member account is ready. Here are your login details:
            </p>

            <table width="100%" cellpadding="0" cellspacing="0" style="background:#f8fafc;border:2px solid #e2e8f0;border-radius:12px;margin:20px 0;">
              <tr><td style="padding:24px;">
                <div style="margin-bottom:16px;">
                  <div style="font-size:11px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:#64748b;margin-bottom:4px;">Email</div>
                  <div style="font-size:16px;font-weight:700;color:#021526;">{email}</div>
                </div>
                <div>
                  <div style="font-size:11px;font-weight:800;letter-spacing:0.1em;text-transform:uppercase;color:#64748b;margin-bottom:4px;">Temporary Password</div>
                  <div style="font-size:24px;font-weight:900;color:#03346E;letter-spacing:0.08em;font-family:monospace;">{temp_password}</div>
                </div>
              </td></tr>
            </table>

            <p style="color:#64748b;font-size:13px;line-height:1.6;margin:0 0 28px;">
              ⚠️ This is a temporary password. Change it anytime after logging in.
            </p>

            <table width="100%" cellpadding="0" cellspacing="0">
              <tr><td align="center" style="padding-bottom:28px;">
                <a href="{login_url}" style="display:inline-block;background:#021526;color:#8BEEE0;text-decoration:none;font-weight:800;font-size:15px;padding:16px 36px;border-radius:8px;">
                  Log in to BuildIT →
                </a>
              </td></tr>
            </table>

            <p style="color:#64748b;font-size:13px;border-top:1px solid #e2e8f0;padding-top:20px;margin:0;">
              Questions? Reply to this email or reach us at
              <a href="mailto:builditconnective@gmail.com" style="color:#03346E;">builditconnective@gmail.com</a>
            </p>
          </td>
        </tr>

        <tr>
          <td style="background:#021526;border-radius:0 0 16px 16px;padding:20px 40px;text-align:center;">
            <p style="color:rgba(253,253,253,0.4);font-size:11px;margin:0;">
              BuildIT Connective · Nairobi, Kenya
            </p>
          </td>
        </tr>

      </table>
    </td></tr>
  </table>
</body>
</html>
"""
    
    text=f"""
Hey {first_name},
Your BuildIT Connective account is ready!

Email: {email}
Password: {temp_password}

Log in: {login_url}
Change password after login: {change_url}


-BuildIT Connective
"""
    return send_email(email,subject, html,text)
    