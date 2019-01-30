import datetime
from django.db import models
from django.db.models import Max
from django.utils import timezone
from django.contrib.auth.models import User, Group

class Folder(models.Model):
	name = models.CharField(max_length=128)
	parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True)


	def __str__(self):
		return self.name


	def home_folder():
		return Folder.objects.get(parent=None)


	def get_folder(id):
		return Folder.objects.get(pk=id)


	def child_folders(self):
		return Folder.objects.get(parent=self.id)


	def child_folders(parent_id):
		return Folder.objects.filter(parent=parent_id)


	def articles(self):
		return  Article.objects.get(folder=self.id)


	def has_parent(self):
		if (self.parent != None):
			return true
		else:
			return false


	def get_parent(self):
		if (self.has_parent):
			return self.parent
		else:
			return None


	# Can the user read the folder?
	def user_can_read(self, user):
		Log.LogMessage('Checking if user can read folder ' + self.name, user.username)

		# First get explicit permissions for folder
		perms = FolderPerm.objects.filter(folder=self)

		if perms:
			for p in perms:
				if user.groups.filter(name=p.group):
					Log.LogMessage('User ' + user.username + ' has permissions to folder ' + self.name + ' through group ' + p.group, user.username)
					return True

		# Second check for default permissions
		perms = FolderPerm.objects.filter(folder=self, group=None)
		if perms:
			for p in perms:
				if p.mode == 'RW':
					return True
				if p.mode == 'R':
					return True
				if p.mode == 'N':
					return False

		# Finally, return True for default
		else:
			Log.LogMessage('Folder ' + self.name + ' has no permissions defined. Defaulting to "R"', user.username)
			return True


	# Can the user write to the folder?
	def user_can_write(self, user):
		Log.LogMessage('Checking if user can write to folder ' + self.name, user.username)

		if (user.is_superuser):
			Log.LogMessage('User has permissions to folder ' + self.name + ' as superuser', user.username)
			return True

		perms = FolderPerm.objects.filter(folder=self)

		# First check for explicit permissions
		if perms:
			for p in perms:
				if user.groups.filter(name=p.group):
					if (p.Mode == 'RW'):
						Log.LogMessage('User has permissions to folder ' + self.name + ' through group ' + p.name, user.username)
						return True
			Log.LogMessage('User has permissions to folder ' + self.name, user.username)
			return False

		# Second check for default permissions
		perms = FolderPerm.objects.filter(folder=self,group=None)
		if perms:
			for p in perms:
				if p.mode == 'RW':
					return True
				if p.mode == 'R':
					return False
				if p.mode == 'N':
					return False

		# Finally, allow reading if nothing is defined
		else:
			Log.LogMessage('Folder ' + self.name + ' has no permissions defined. Defaulting to "R".', user.username)
			return False


	# Return list of folders leading up to this folder
	def path(self):
		this_folder = self
		full_path = [this_folder]

		while this_folder.parent != None:
			this_folder = this_folder.parent
			full_path += [this_folder]

		full_path.reverse()
		return full_path


	# Return full path as a single string, not as a list
	def path_text(self):
		full_path = self.path()

		full_path.reverse()
		return "/".join(full_path)


	def init():
		# Do we have a 'Home' folder?
		home = Folder.objects.filter(name='Home')

		# Create root folder if non-existant
		if not home:
			Log.LogMessage("No home folder exists! Creating one...")
			home_folder = Folder(name='Home', parent=None)
			home_folder.save()

		# Do we have an 'Admin' group?
		admins = Group.objects.filter(name='Administrators')

		# Create group if non-existant
		if not admins:
			Log.LogMessage("Administrators group does not exist! Creating one...")
			admin_group = Group(name='Administrators')
			admin_group.save()

			Log.LogMessage("Adding superuser(s) to Administrators group...")
			admin_users = User.objects.filter(is_superuser=True)
			for u in admin_users:
				Log.LogMessage("... Added " + u.username)
				u.groups.add(admin_group)
				u.save()

		return None


# Define explicit permissions for folders
# By default, all users can read
# By default, all admins can create/edit
class FolderPerm(models.Model):
	folder = models.ForeignKey(Folder, on_delete=models.CASCADE)
	group = models.ForeignKey(Group, on_delete=models.CASCADE, null=True) # Importing Django's native group system, null group is default permissions for all users
	mode = models.CharField(max_length=2)	# N = None, R = Read, RW = Read/Write


class Article(models.Model):
	folder = models.ForeignKey(Folder, on_delete=models.CASCADE)

	def __str__(self):
		active_version = self.active_version()
		return active_version.title

	def deactivate_all_versions(self):
		all_versions = History.objects.filter(article=self)

		for v in all_versions:
			v.is_active = False
			v.save()

	def version_history(self):
		article_history = History.objects.filter(article=self)
		return article_history

	def newest_ver(self):
		newest_article_history = History.objects.filter(article=self).order_by('-version')[0]
		return newest_article_history.version

	def active_version(self):
		return History.objects.get(article=self, is_active=True)


class History(models.Model):
	title = models.CharField(max_length=256)
	article = models.ForeignKey(Article, on_delete=models.CASCADE)
	version = models.IntegerField(default=1)
	pub_date = models.DateTimeField('date published')
	content = models.TextField()
	author = models.CharField(max_length=128)
	is_active = models.BooleanField(default=False)


	def get_active_ver(self):
		return History.objects.get(article=self.article, is_active=True)


	def set_active(self):
		self.is_active = True
		self.save()


	def __str__(self):
		return str(self.article.id) + ' v' + str(self.version) + ' - ' + self.title


class Log(models.Model):
	timestamp = models.DateTimeField(default=timezone.now)
	user = models.CharField(max_length=256, default='SYSTEM')
	message = models.CharField(max_length=1024)


	def LogMessage(text, user='SYSTEM'):
		new_entry = Log(message=text, user=user)
		new_entry.save()


	def __str__(self):
		log_string = "[" + str(self.timestamp) + "] - " + self.user + " - " + self.message
		return log_string
