const express = require('express');
const cors = require('cors');
const fs = require('fs');
const path = require('path');
const app = express();
const PORT = 3000;

app.use(cors({ origin: '*' }));
app.use(express.urlencoded({ extended: true }));
app.use(express.json());

const USERS_FILE = path.join(__dirname, 'users.json');
const PROTECTED_FILE = path.join(__dirname, 'protected.js');

function loadUsers() {
  if (!fs.existsSync(USERS_FILE)) return {};
  return JSON.parse(fs.readFileSync(USERS_FILE, 'utf8'));
}

function saveUsers(users) {
  fs.writeFileSync(USERS_FILE, JSON.stringify(users, null, 2));
}

app.get('/check-access', (req, res) => {
  const email = req.query.email;
  if (!email) return res.status(400).send('// No email provided');

  const users = loadUsers();

  if (!users[email]) {
    users[email] = { status: 'pending', timestamp: new Date().toISOString() };
    saveUsers(users);
    return res.status(403).send('// Access pending approval. Contact admin.');
  }

  if (users[email].status === 'approved') {
    const script = fs.readFileSync(PROTECTED_FILE, 'utf8');
    res.setHeader('Content-Type', 'application/javascript');
    return res.send(script);
  }

  return res.status(403).send(`// Access ${users[email].status}`);
});

app.get('/admin', (req, res) => {
  const users = loadUsers();
  const rows = Object.entries(users).map(([email, info]) => `
    <tr>
      <td>${email}</td>
      <td>${info.status}</td>
      <td>${info.timestamp}</td>
      <td>
        <form method="POST" action="/action">
          <input type="hidden" name="email" value="${email}">
          <button name="decision" value="approved" ${info.status === 'approved' ? 'disabled' : ''}>✅</button>
          <button name="decision" value="rejected" ${info.status === 'rejected' ? 'disabled' : ''}>❌</button>
        </form>
      </td>
    </tr>
  `).join('');

  res.send(`
    <html>
      <head>
        <title>Access Control Admin Panel</title>
        <style>
          body {
            font-family: Arial, sans-serif;
            padding: 20px;
            background: #f8f9fa;
          }
          h2 {
            text-align: center;
          }
          table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            font-size: 16px;
            background: white;
          }
          th, td {
            border: 1px solid #ddd;
            padding: 12px 16px;
            text-align: left;
          }
          th {
            background-color: #343a40;
            color: white;
          }
          tr:nth-child(even) {
            background-color: #f2f2f2;
          }
          button {
            padding: 6px 12px;
            margin-right: 8px;
            font-weight: bold;
            border-radius: 4px;
            border: none;
            cursor: pointer;
          }
          button[value="approved"] {
            background-color: #28a745;
            color: white;
          }
          button[value="rejected"] {
            background-color: #dc3545;
            color: white;
          }
          button[disabled] {
            opacity: 0.5;
            cursor: not-allowed;
          }
        </style>
      </head>
      <body>
        <h2>🔐 Admin Panel – Bookmarklet Access</h2>
        <table>
          <thead>
            <tr><th>Email</th><th>Status</th><th>Requested At</th><th>Actions</th></tr>
          </thead>
          <tbody>
            ${rows || '<tr><td colspan="4">No requests found</td></tr>'}
          </tbody>
        </table>
      </body>
    </html>
  `);
});

app.post('/action', (req, res) => {
  const { email, decision } = req.body;

  const users = loadUsers();
  if (users[email]) {
    users[email].status = decision;
    saveUsers(users);
  }

  res.redirect('/admin');
});

app.listen(PORT, () => console.log(`✅ Server running at http://localhost:${PORT}`));
