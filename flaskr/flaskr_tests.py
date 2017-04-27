import os
import flaskr
import unittest
import tempfile

class FlaskrTestCase(unittest.TestCase):
	def setUp(self):
		self.db_fd, flaskr.app.config["DATABASE"] = tempfile.mkstemp()
		flaskr.app.config["TESTING"] = True
		self.app = flaskr.app.test_client()
		with flaskr.app.app_context():
			flaskr.init_db()

	def tearDown(self):
		os.close(self.db_fd)
		os.unlink(flaskr.app.config["DATABASE"])

	def login(self, username, password):
		return self.app.post("/login", data=dict(
			username=username,
			password=password
		), follow_redirects=True)

	def logout(self):
		return self.app.get("/logout", follow_redirects=True)

	def test_empty_db(self):
		rv = self.app.get("/")
		# print(rv.data)
		self.assertIn(b"What! There ain't any entries yet.", rv.data)

	def test_login_logout(self):
		rv = self.login("admin", "default")
		self.assertIn(b"You are now logged in!", rv.data)
		rv = self.logout()
		self.assertIn(b"You are now logged out! Bye!", rv.data)
		rv = self.login("bad", "default")
		self.assertIn(b"Wrong username", rv.data)
		rv = self.login("admin", "bad")
		self.assertIn(b"Wrong password", rv.data)

	def test_messages(self):
		self.login("admin", "default")
		rv = self.app.post("/add", data=dict(
			title="<Hello>",
			text="<strong>HTML</strong> allowed here"
		), follow_redirects=True)
		self.assertNotIn(b"What! There ain't any entries yet.", rv.data)
		self.assertIn(b"&lt;Hello&gt;", rv.data)
		self.assertIn(b"<strong>HTML</strong> allowed here", rv.data)

if __name__ == '__main__':
	unittest.main()