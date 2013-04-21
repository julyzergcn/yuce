# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'User'
        db.create_table(u'core_user', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('password', self.gf('django.db.models.fields.CharField')(max_length=128)),
            ('last_login', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('is_superuser', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('username', self.gf('django.db.models.fields.CharField')(unique=True, max_length=30)),
            ('first_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('last_name', self.gf('django.db.models.fields.CharField')(max_length=30, blank=True)),
            ('email', self.gf('django.db.models.fields.EmailField')(max_length=75, blank=True)),
            ('is_staff', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('is_active', self.gf('django.db.models.fields.BooleanField')(default=True)),
            ('date_joined', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('score', self.gf('django.db.models.fields.DecimalField')(default=1000, max_digits=20, decimal_places=8)),
            ('last_login_ip', self.gf('django.db.models.fields.CharField')(max_length=20, blank=True)),
        ))
        db.send_create_signal(u'core', ['User'])

        # Adding M2M table for field groups on 'User'
        db.create_table(u'core_user_groups', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'core.user'], null=False)),
            ('group', models.ForeignKey(orm[u'auth.group'], null=False))
        ))
        db.create_unique(u'core_user_groups', ['user_id', 'group_id'])

        # Adding M2M table for field user_permissions on 'User'
        db.create_table(u'core_user_user_permissions', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('user', models.ForeignKey(orm[u'core.user'], null=False)),
            ('permission', models.ForeignKey(orm[u'auth.permission'], null=False))
        ))
        db.create_unique(u'core_user_user_permissions', ['user_id', 'permission_id'])

        # Adding model 'Activity'
        db.create_table(u'core_activity', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'])),
            ('action', self.gf('django.db.models.fields.CharField')(max_length=20)),
            ('action_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('content_type', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['contenttypes.ContentType'], null=True, blank=True)),
            ('object_id', self.gf('django.db.models.fields.PositiveIntegerField')(null=True, blank=True)),
            ('text', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
        ))
        db.send_create_signal(u'core', ['Activity'])

        # Adding model 'Tag'
        db.create_table(u'core_tag', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('tag', self.gf('django.db.models.fields.CharField')(max_length=20)),
        ))
        db.send_create_signal(u'core', ['Tag'])

        # Adding model 'Topic'
        db.create_table(u'core_topic', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'])),
            ('subject', self.gf('django.db.models.fields.CharField')(max_length=200)),
            ('subject_english', self.gf('django.db.models.fields.CharField')(max_length=200, blank=True)),
            ('content', self.gf('django.db.models.fields.TextField')()),
            ('content_english', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('status', self.gf('django.db.models.fields.CharField')(default='pending', max_length=20)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
            ('deadline', self.gf('django.db.models.fields.DateTimeField')()),
            ('event_close_date', self.gf('django.db.models.fields.DateTimeField')()),
            ('complete_date', self.gf('django.db.models.fields.DateTimeField')(null=True, blank=True)),
            ('end_weight', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('text', self.gf('django.db.models.fields.TextField')(blank=True)),
            ('yesno', self.gf('django.db.models.fields.NullBooleanField')(null=True, blank=True)),
        ))
        db.send_create_signal(u'core', ['Topic'])

        # Adding M2M table for field tags on 'Topic'
        db.create_table(u'core_topic_tags', (
            ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True)),
            ('topic', models.ForeignKey(orm[u'core.topic'], null=False)),
            ('tag', models.ForeignKey(orm[u'core.tag'], null=False))
        ))
        db.create_unique(u'core_topic_tags', ['topic_id', 'tag_id'])

        # Adding model 'Bet'
        db.create_table(u'core_bet', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.User'])),
            ('topic', self.gf('django.db.models.fields.related.ForeignKey')(to=orm['core.Topic'])),
            ('score', self.gf('django.db.models.fields.DecimalField')(max_digits=20, decimal_places=8)),
            ('weight', self.gf('django.db.models.fields.PositiveIntegerField')()),
            ('yesno', self.gf('django.db.models.fields.BooleanField')(default=False)),
            ('created_date', self.gf('django.db.models.fields.DateTimeField')(default=datetime.datetime.now)),
        ))
        db.send_create_signal(u'core', ['Bet'])


    def backwards(self, orm):
        # Deleting model 'User'
        db.delete_table(u'core_user')

        # Removing M2M table for field groups on 'User'
        db.delete_table('core_user_groups')

        # Removing M2M table for field user_permissions on 'User'
        db.delete_table('core_user_user_permissions')

        # Deleting model 'Activity'
        db.delete_table(u'core_activity')

        # Deleting model 'Tag'
        db.delete_table(u'core_tag')

        # Deleting model 'Topic'
        db.delete_table(u'core_topic')

        # Removing M2M table for field tags on 'Topic'
        db.delete_table('core_topic_tags')

        # Deleting model 'Bet'
        db.delete_table(u'core_bet')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'core.activity': {
            'Meta': {'object_name': 'Activity'},
            'action': ('django.db.models.fields.CharField', [], {'max_length': '20'}),
            'action_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']", 'null': 'True', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'object_id': ('django.db.models.fields.PositiveIntegerField', [], {'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"})
        },
        u'core.bet': {
            'Meta': {'object_name': 'Bet'},
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'score': ('django.db.models.fields.DecimalField', [], {'max_digits': '20', 'decimal_places': '8'}),
            'topic': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.Topic']"}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'weight': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'yesno': ('django.db.models.fields.BooleanField', [], {'default': 'False'})
        },
        u'core.tag': {
            'Meta': {'object_name': 'Tag'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'tag': ('django.db.models.fields.CharField', [], {'max_length': '20'})
        },
        u'core.topic': {
            'Meta': {'object_name': 'Topic'},
            'complete_date': ('django.db.models.fields.DateTimeField', [], {'null': 'True', 'blank': 'True'}),
            'content': ('django.db.models.fields.TextField', [], {}),
            'content_english': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'created_date': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'deadline': ('django.db.models.fields.DateTimeField', [], {}),
            'end_weight': ('django.db.models.fields.PositiveIntegerField', [], {}),
            'event_close_date': ('django.db.models.fields.DateTimeField', [], {}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'status': ('django.db.models.fields.CharField', [], {'default': "'pending'", 'max_length': '20'}),
            'subject': ('django.db.models.fields.CharField', [], {'max_length': '200'}),
            'subject_english': ('django.db.models.fields.CharField', [], {'max_length': '200', 'blank': 'True'}),
            'tags': ('django.db.models.fields.related.ManyToManyField', [], {'symmetrical': 'False', 'to': u"orm['core.Tag']", 'null': 'True', 'blank': 'True'}),
            'text': ('django.db.models.fields.TextField', [], {'blank': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['core.User']"}),
            'yesno': ('django.db.models.fields.NullBooleanField', [], {'null': 'True', 'blank': 'True'})
        },
        u'core.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_login_ip': ('django.db.models.fields.CharField', [], {'max_length': '20', 'blank': 'True'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'score': ('django.db.models.fields.DecimalField', [], {'default': '1000', 'max_digits': '20', 'decimal_places': '8'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        }
    }

    complete_apps = ['core']