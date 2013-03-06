<html>
  <head>
    <title>Login</title>
  <body>
    <h1>Login</h1>
    <div id="login_form">
      <form action="${login_url}" method="POST">
        <input type="hidden" name="endpoint" value="${endpoint}"/>
        <input type="hidden" name="auth_session_key" value="${auth_session_key}"/>
        <input type="hidden" name="form.submitted" value="${form_submitted}"/>
        <div id="login_form.username">
          <label for="post.username">Username</label>
          <input id="post.username" type="text" name="login"/>
        </div>
        <div id="login_form.password">
          <label for="post.password">Password</label>
          <input id="post.password" type="password" name="password"/>
        </div>
        <input type="submit" value="Login"/>
      </form>
    </div>
  </body>
</html>
