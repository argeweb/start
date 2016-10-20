#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Created with YooLiang Technology (侑良科技).
# Author: Qi-Liang Wen (温啓良）
# Web: http://www.yooliang.com/
# Date: 2015/7/12.
from argeweb.libs import wtforms
from cgi import escape

html_params = wtforms.widgets.html_params
HTMLString = wtforms.widgets.HTMLString
text_type = wtforms.compat.text_type
class MultipleReferenceCheckboxWidget(object):
    """
    Widget for MultipleReferenceField. Displays options as checkboxes"""
    def __init__(self, html_tag='div'):
        self.html_tag = html_tag

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs['class'] = kwargs.get('class', '').replace('span6', '')
        html = [u'<%s %s>'
            % (self.html_tag, html_params(**kwargs))]
        for subfield in field:
            html.append(u'<label class="checkbox" for="%s">%s %s</label>'
                % (subfield.label.field_id, subfield(), subfield.label.text))
        html.append(u'</%s>' % self.html_tag)
        return HTMLString(u''.join(html))


class RichTextWidget(object):
    html_params = staticmethod(html_params)
    """
    Widget for MultipleReferenceField. Displays options as checkboxes"""
    def __init__(self, html_tag='textarea'):
        super(RichTextWidget, self).__init__()
        self.html_tag = html_tag

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.id)
        kwargs['class'] = kwargs.get('class', '').replace('span6', '') + " editor"
        if field.data == "None" or field.data is None:
            field.data = ""
        html = u'<%s %s>%s</%s>'% (
            self.html_tag, html_params(**kwargs),
            field.data, self.html_tag
        )
        return HTMLString(html)


class ImageSelectWidget(object):
    html_params = staticmethod(html_params)
    """
    Widget for MultipleReferenceField. Displays options as checkboxes"""
    def __init__(self, html_tag='input'):
        super(ImageSelectWidget, self).__init__()
        self.html_tag = html_tag

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.id)
        kwargs['class'] = kwargs.get('class', '').replace('span6', 'form-control') + " image"
        if field.data == "None" or field.data is None:
            field.data = ""
        if field.data:
            field_data = field.data
        else:
            field_data = ""
        html = u"""
        <div class="img_selector_div input-group">
            <%s type="text" %s value="%s" />
            <div class="input-group-btn">
                <div class="btn btn-outline img_selector_item" style="background-image: url(%s);"></div>
            </div>
            <a href="#" class="btn btn-info filepicker"><i class="fa fa-photo"></i> 選取</a>
        </div>
        """ % (self.html_tag, html_params(**kwargs), field_data, field_data)
        return HTMLString(html)


class ImagesSelectWidget(object):
    html_params = staticmethod(html_params)
    """
    Widget for MultipleReferenceField. Displays options as checkboxes"""
    def __init__(self, html_tag='textarea'):
        super(ImagesSelectWidget, self).__init__()
        self.html_tag = html_tag

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.id)
        kwargs['class'] = kwargs.get('class', '').replace('span6', '') + " images"
        if field.data == "None" or field.data is None:
            field.data = ""
        list = field.data.split(";")
        html = u'<div class="imgs_selector_div">' \
               u'<%s %s style="display:none" >%s</%s>' \
               u'<a data-target="%s" class="btn-images-open-dropbox">Dropbox</a>'\
               u'<a data-target="%s" class="btn-images-open-google-picker">Google相冊</a>'\
               u'<a data-target="%s" class="btn-images-open-server">伺服器</a>' \
               u'<div class="img_selector_sp"></div>'\
               % (self.html_tag, html_params(**kwargs), field.data, self.html_tag, field.id, field.id, field.id,)
        for item in list:
            if item != u"":
                html += u'<div class="img_selector_item" data-link="%s" style="background-image: url(%s);" />' % (item, item)
        return HTMLString(html + "</div>")



class CategorySelectWidget(object):
    """
    Renders a select field.

    If `multiple` is True, then the `size` property should be specified on
    rendering to make the field useful.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected)`.
    """
    def __init__(self, multiple=False):
        self.multiple = multiple

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected in field.iter_choices():
            return_item = self.render_option(val, label, selected)
            if return_item:
                html.append(return_item)
        html.append('</select>')
        return HTMLString(''.join(html))

    @classmethod
    def render_option(cls, value, label, selected, **kwargs):
        if value is True:
            # Handle the special case of a 'True' value.
            value = text_type(value)

        options = dict(kwargs, value=value)
        if selected:
            options['selected'] = True
        if value == '__None':
            return HTMLString('<option %s>%s</option>' % (html_params(**options), escape(text_type(label))))
        else:
            if hasattr(label, "level") and hasattr(label, "name"):
                if label.level == 9999 and label.name == u'super_monkey' and (selected is False or selected is None):
                    return None
            return HTMLString('<option %s>%s</option>' % (html_params(**options), escape(text_type(label.title))))


class Option(object):
    """
    Renders the individual option from a select field.

    This is just a convenience for various custom rendering situations, and an
    option by itself does not constitute an entire field.
    """
    def __call__(self, field, **kwargs):
        return CategorySelectWidget.render_option(field._value(), field.label.text, field.checked, **kwargs)


class HiddenWidget(object):
    html_params = staticmethod(html_params)
    """
    Widget for MultipleReferenceField. Displays options as checkboxes"""
    def __init__(self, html_tag='input'):
        super(HiddenWidget, self).__init__()
        self.html_tag = html_tag

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        kwargs.setdefault('name', field.id)
        kwargs['class'] = kwargs.get('class', '').replace('span6', 'form-control') + " image"
        if field.data == "None" or field.data is None:
            field.data = ""
        if field.data:
            field_data = field.data
        else:
            field_data = ""
        html = u"""
        <div class="img_selector_div input-group">
            <%s type="text" %s value="%s" />
            <div class="input-group-btn">
                <div class="btn btn-outline img_selector_item" style="background-image: url(%s);" /></div>
                <a href="#" class="btn btn-info filepicker"><i class="fa fa-photo"></i> 選取</a>
            </div>
        </div>
        """ % (self.html_tag, html_params(**kwargs), field_data, field_data)
        return HTMLString(html)