// m70_mini_netflix.js

function togglePassword() {
    var pw = document.getElementById('password');
    pw.type = pw.type === 'password' ? 'text' : 'password';
}

function generatePassword() {
    var length = 16;
    var charset = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()-_=+?";
    var password = "";
    for (var i = 0, n = charset.length; i < length; ++i) {
        password += charset.charAt(Math.floor(Math.random() * n));
    }
    document.getElementById('password').value = password;
}

function toggleUserPassword(id, pw) {
    var span = document.getElementById('pw-' + id);
    if (span.innerText.startsWith('*')) {
        span.innerText = pw;
    } else {
        span.innerText = '*'.repeat(pw.length);
    }
}

