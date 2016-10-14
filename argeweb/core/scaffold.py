#!/usr/bin/env python
# -*- coding: utf-8 -*-
from argeweb.core import inflector
from argeweb.core.gaeforms import model_form
from argeweb.components.flash_messages import FlashMessages
from google.appengine.ext.ndb.google_imports import datastore_errors
#, autoadmin
#(autoadmin)  # load autoadmin here, if any controller use scaffold it'll be included and initialized

def generate_upload_url(success_path):
    from google.appengine.ext import blobstore
    from argeweb import settings
    cloud_storage_bucket = ""
    if settings.get('upload').get('use_cloud_storage'):
        cloud_storage_bucket = settings.get('upload', {}).get('bucket')
    return blobstore.create_upload_url(
            success_path= success_path,
            gs_bucket_name=cloud_storage_bucket)

class Scaffolding(object):
    """
    Scaffolding Component
    """

    def __init__(self, controller):
        self.controller = controller
        self._init_meta()
        self._init_flash()

    def _init_flash(self):
        if not FlashMessages in self.controller.Meta.components:
            self.controller.components['flash_messages'] = FlashMessages(self.controller)

    def _init_meta(self):
        """
        Constructs the controller's scaffold property from the controller's Scaffold class.
        If the controller doens't have a scaffold, uses the automatic one.
        """

        if not hasattr(self.controller.Meta, 'Model'):
            _load_model(self.controller)

        if not hasattr(self.controller, 'Scaffold'):
            setattr(self.controller, 'Scaffold', Scaffold)

        plugins_helper = self.controller.plugins.get_helper(self.controller)
        if plugins_helper is not None:
            try:
                titles = plugins_helper["controllers"][str(self.controller.name).split(".")[-1]]["actions"]
                setattr(self.controller.Scaffold, "title", titles)
            except:
                setattr(self.controller.Scaffold, "title", u"Unknown")


        if not issubclass(self.controller.Scaffold, Scaffold):
            self.controller.Scaffold = type('Scaffold', (self.controller.Scaffold, Scaffold), {})

        setattr(self.controller, 'scaffold', self.controller.Scaffold(self.controller))

        self.controller.events.template_names += self._on_template_names
        self.controller.events.before_render += self._on_before_render
        self.controller.events.scaffold_before_parse += self._on_scaffold_before_parse

    def _on_scaffold_before_parse(self, controller):
        if not hasattr(controller.meta, 'Form') or not controller.meta.Form:
            controller.meta.Form = controller.scaffold.ModelForm

    def _on_template_names(self, controller, templates):
        """Injects scaffold templates into the template list"""

        controller, prefix, action, ext = self.controller.route.name, self.controller.route.prefix, self.controller.route.action, self.controller.meta.view.template_ext

        # Try the prefix template first
        if prefix:
            templates.append('scaffolding/%s_%s.%s' % (prefix, action, ext))

        # Then try the non-prefix one.
        templates.append('scaffolding/%s.%s' % (action, ext))

    def _on_before_render(self, controller):
        scaffold_title = {}
        try:
            if hasattr(controller.scaffold, "title"):
                scaffold_title_temp = controller.scaffold.title
                if hasattr(scaffold_title_temp, "items"):
                    scaffold_title = scaffold_title_temp
                    for item in scaffold_title_temp:
                        scaffold_title.append(item)
                else:
                    for item in scaffold_title_temp:
                        scaffold_title[item["action"]] = item["name"]
        except:
            pass
        try:
            scaffold_description = controller.scaffold.description
        except AttributeError:
            scaffold_description = {}
        try:
            scaffold_field_name = controller.scaffold.field_name
        except AttributeError:
            scaffold_field_name = {}
        scaffold_languages = []
        languages = {
            "zhtw": {"lang":"zhtw", "title": u"繁體中文"},
            "zhcn": {"lang":"zhcn", "title": u"简体中文"},
            "enus": {"lang":"enus", "title": u"英語"},
        }
        try:
            for lang in controller.scaffold.languages:
                scaffold_languages.append(languages[lang])
        except AttributeError:
            pass

        controller.context['scaffolding'] = {
            'name': controller.name,
            'proper_name': controller.proper_name,
            'scaffold_title': scaffold_title,
            'scaffold_description': scaffold_description,
            'scaffold_field_name': scaffold_field_name,
            'scaffold_language': scaffold_languages,
            'plural': controller.scaffold.plural,
            'singular': controller.scaffold.singular,
            'form_action': controller.scaffold.form_action,
            'form_encoding': controller.scaffold.form_encoding,
            'display_properties': controller.scaffold.display_properties,
            'display_properties_in_list': controller.scaffold.display_properties_in_list,
            'layouts': controller.scaffold.layouts,
            'navigation': controller.scaffold.navigation
        }


class Scaffold(object):
    """
    Scaffold Meta Object Base Class
    """
    def __init__(self, controller):
        display_properties, model_form_data, redirect_url = None, None, None
        if hasattr(controller.meta, "Model"):
            display_properties=sorted([name for name, property in controller.meta.Model._properties.items()])
            model_form_data=model_form(controller.meta.Model)
        try:
            redirect_url = controller.uri(action='list') if controller.uri_exists(action='list') else None
        except KeyError:
            pass

        defaults = dict(
            query_factory=default_query_factory,
            create_factory=default_create_factory,
            title=inflector.titleize(controller.proper_name),
            plural=inflector.underscore(controller.name),
            singular=inflector.underscore(inflector.singularize(controller.name)),
            ModelForm=model_form_data,
            display_properties=display_properties,
            display_properties_in_list=display_properties,
            redirect=redirect_url,
            form_action=None,
            form_encoding='application/x-www-form-urlencoded',
            flash_messages=True,
            layouts={
                None: 'layouts/default.html',
            },
            navigation={},
            field_name={
                "created": u"建立時間",
                "modified": u"修改時間",
                "sort": u"排序值",
                "is_enable": u"啟用"
            }
        )
        try:
            defaults["field_name"].update(controller.meta.Model.Meta.label_name)
        except:
            pass

        for k, v in defaults.iteritems():
            if not hasattr(self, k):
                setattr(self, k, v)


# Default Factories


def default_query_factory(controller):
    """
    The default factory just returns Model.query(), sorted by created if it's available.
    """
    Model = controller.meta.Model
    query = Model.query()
    if 'sort' in Model._properties and Model._properties['sort']._indexed:
        query = query.order(-Model.sort)
    else:
        if 'created' in Model._properties and Model._properties['created']._indexed:
            query = query.order(-Model.created)

    return query


def default_create_factory(controller):
    """
    The default create factory just calls Model()
    """
    return controller.meta.Model()


def delegate_query_factory(controller):
    """
    Calls Model.Meta.query_factory or Model.list or Model.query.
    """
    Model = controller.Meta.Model
    if hasattr(Model.Meta, 'query_factory'):
        return Model.Meta.query_factory(controller)
    if hasattr(Model, 'list'):
        return Model.list(controller)
    return default_query_factory(controller)


def delegate_create_factory(controller):
    """
    Calls Model.Meta.create_factory or Model.create or the Model constructor.
    """
    Model = controller.Meta.Model
    if hasattr(Model.Meta, 'create_factory'):
        return Model.Meta.create_factory(controller)
    if hasattr(Model, 'create'):
        return Model.create(controller)
    return default_create_factory(controller)


# Utility Functions


def _load_model(controller):
    # Attempt to import the model automatically
    model_name = controller.__class__.__name__ + 'Model'
    try:
        import_form_base = str(controller.__module__)
        module = __import__(import_form_base, fromlist=['*'])
        setattr(controller.Meta, 'Model', getattr(module, model_name))
    except (ImportError, AttributeError):
        try:
            import_form_base = '.'.join(controller.__module__.split('.')[:-2])
            s = '%s.models.%s' % (import_form_base, inflector.underscore(model_name))
            module = __import__(s, fromlist=['*'])
            setattr(controller.Meta, 'Model', getattr(module, model_name))
        except (ImportError, AttributeError, ValueError):
            import logging
            logging.debug("Scaffold coudn't automatically determine a model class for controller %s, please assign it a Meta.Model class variable." % controller.__class__.__name__)


def _flash(controller, *args, **kwargs):
    if 'flash_messages' in controller.components and controller.scaffold.flash_messages:
        controller.components.flash_messages(*args, **kwargs)


# controller Methods
def list(controller):
    plural = None
    if 'query' in controller.request.params:
        try:
            plural = controller.components.search()
        except:
            plural = controller.scaffold.query_factory(controller)
    else:
        try:
            plural = controller.scaffold.query_factory(controller)
        except:
            pass
    controller.context.set(**{controller.scaffold.plural: plural})
    if controller.scaffold.plural in controller.context:
        try:
            last_record = None
            lst = controller.context[controller.scaffold.plural]
            if lst.__class__.__name__ == "list":
                last_record = lst[-1]
            else:
                lst_record = lst.fetch()
                if len(lst_record) > 0:
                    last_record = lst_record[-1]
            if last_record:
                controller.context["last_record_date"] = last_record.modified
        except:
            pass


def view(controller, key):
    item = controller.util.decode_key(key).get()
    if not item:
        return 404
    controller.context["last_record_date"] = item.modified
    controller.context.set(**{
        controller.scaffold.singular: item})


def save_callback(controller, item, parser):
    parser.update(item)
    controller.events.scaffold_before_save(controller=controller, container=parser.container, item=item)
    item.put()
    controller.events. scaffold_after_save(controller=controller, container=parser.container, item=item)


def parser_action(controller, item, callback=save_callback):
    controller.events.scaffold_before_parse(controller=controller)
    parser = controller.parse_request(fallback=item)

    if controller.request.method in ('PUT', 'POST', 'PATCH'):
        controller.response.headers["Request-Method"] = controller.request.method
        controller.events.scaffold_before_validate(controller=controller, parser=parser, item=item)
        if parser.validate():
            controller.events.scaffold_before_apply(controller=controller, container=parser.container, item=item)
            callback(controller, item, parser)
            controller.events.scaffold_after_apply(controller=controller, container=parser.container, item=item)
            response_data = {
                "response_info": "success",
                "response_method": controller.params.get_string("routeAction"),
            }
            if "data" in controller.context:
                controller.context["data"].update(response_data)
            else:
                controller.context["data"] = response_data
            controller.context.set(**{
                controller.scaffold.singular: item,
            })
            _flash(controller, u'項目已儲存', 'success')

            if controller.scaffold.redirect:
                return controller.redirect(controller.scaffold.redirect)
        else:
            controller.context['errors'] = parser.errors
            response_data = {
                "errors": parser.errors,
                "method": controller.params.get_string("routeAction"),
            }
            if "data" in controller.context:
                controller.context["data"].update(response_data)
            else:
                controller.context["data"] = response_data
            _flash(controller, u'表單欄位的值有誤，請確認後再試一次', 'error')

    # 檢查是否有語系欄位
    lang = []
    for field in parser.container._fields:
        if field.find("_lang_") > 0:
            field_name, field_lang = field.split("_lang_")
            if field_lang not in lang:
                lang.append(field_lang)
    controller.scaffold.languages = lang
    controller.context.set(**{
        'form': parser.container,
        controller.scaffold.singular: item})
    if controller.params.get_string("returnType") == u"json" or controller.request.content_type == 'application/json':
        controller.meta.change_view("json")


def add(controller):
    item = controller.scaffold.create_factory(controller)
    controller.scaffold.redirect = False
    return parser_action(controller, item)


def edit(controller, key):
    item = controller.util.decode_key(key).get()
    if not item:
        return 404
    controller.context["last_record_date"] = item.modified
    controller.scaffold.redirect = False
    return parser_action(controller, item)


def delete(controller, key):
    controller.response.headers["Request-Method"] = 'DELETE'
    key = controller.util.decode_key(key)
    controller.events.scaffold_before_delete(controller=controller, key=key)
    key.delete()
    controller.events.scaffold_after_delete(controller=controller, key=key)
    _flash(controller, u'此項目已成功的刪除', 'success')
    if controller.scaffold.redirect:
        import time
        controller.response.headers["Command-Redirect"] = controller.scaffold.redirect + "?rnid=" + str(time.time())
        controller.meta.change_view("json")
        controller.context["data"] = {"info": "success"}


def sort_up(controller, key):
    item = controller.util.decode_key(key).get()
    if not item:
        return 404
    cursor = "False"
    if "cursor" in controller.request.params:
        cursor = controller.request.params.get("cursor")
    if "category" in controller.request.params:
        cat_str = controller.request.params.get("category")
        prev_item = controller.meta.Model.get_prev_one_with_category(item, cat_str)
        redirect_path = controller.uri(action='list', category=cat_str, cursor=cursor)
    else:
        prev_item = controller.meta.Model.get_prev_one(item)
        redirect_path = controller.uri(action='list', cursor=cursor)

    if prev_item is not None:
        sort = prev_item.sort
        prev_item.sort = item.sort
        item.sort = sort
        prev_item.put()
        item.put()
    controller.meta.change_view("json")
    controller.response.headers["Command-Redirect"] = redirect_path
    controller.context["data"] = {"info": "success"}


def sort_down(controller, key):
    item = controller.util.decode_key(key).get()
    if not item:
        return 404
    cursor = "False"
    if "cursor" in controller.request.params:
        cursor = controller.request.params.get("cursor")
    if "category" in controller.request.params:
        cat_str = controller.request.params.get("category")
        next_item = controller.meta.Model.get_next_one_with_category(item, cat_str)
        redirect_path = controller.uri(action='list', category=cat_str, cursor=cursor)
    else:
        next_item = controller.meta.Model.get_next_one(item)
        redirect_path = controller.uri(action='list', cursor=cursor)
    if next_item is not None:
        sort = next_item.sort
        next_item.sort = item.sort
        item.sort = sort
        next_item.put()
        item.put()
    controller.meta.change_view("json")
    controller.response.headers["Command-Redirect"] = redirect_path
    controller.context["data"] = {"info": "success"}


def set_boolean_field(controller, key):
    controller.meta.change_view("json")
    item = controller.util.decode_key(key).get()
    field_name = controller.params.get_string("field")
    field_value = controller.params.get_boolean("value")
    controller.context["data"] = {"info": "failure"}
    if not item:
        return

    if hasattr(item, field_name):
        try:
            setattr(item, field_name, field_value)
        except:
            return
        item.put()
        controller.context["data"] = {"info": "success"}


def plugins_check(controller):
    controller.meta.change_view('jsonp')
    controller.context['data'] = {
        'status': "enable"
    }