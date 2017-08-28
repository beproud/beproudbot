import factory

from db import RedmineUser, ProjectChannel


class RedmineUserFactory(factory.Factory):
    class Meta:
        model = RedmineUser


class ProjectChannelFactory(factory.Factory):
    class Meta:
        model = ProjectChannel
