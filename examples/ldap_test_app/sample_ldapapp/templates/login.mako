<!doctype html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <title>Auth Page</title>
</head>
<body>

<%def name="form(name, title)">
<form id="${name}" method="post" action="http://localhost:8521/login/${ name }">
    <input type="submit" value="${title}" />
    <input type="hidden" name="endpoint" value="${request.route_url('logged_in')}" />
    <input type="hidden" name="auth_session_key" value="zzaaa" />
</form>
</%def>

${form('facebook', 'Login with Facebook')}
${form('github', 'Login with Github')}
${form('twitter', 'Login with Twitter')}
${form('bitbucket', 'Login with Bitbucket')}
${form('google', 'Login with Google')}
${form('yahoo', 'Login with Yahoo')}
${form('live', 'Login with Windows Live')}
${form('ldap', 'Login with ldap')}

</body>
</html>
