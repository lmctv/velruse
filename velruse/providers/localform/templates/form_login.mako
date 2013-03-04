<html>
  <head>
    <title>LDAP login</title>
  <body>
    <form action="${login_url}" method="POST">
      <input type="hidden" name="endpoint" value="${endpoint}">
      <input type="hidden" name="auth_session_key" value="${auth_session_key}">
      <input type="hidden" name="form.submitted" value="${form_submitted}">
      <input type="text" name="login">
      <input type="password" name="password">
      <input type="submit" value="LDAP login">
  </body>
</html>
