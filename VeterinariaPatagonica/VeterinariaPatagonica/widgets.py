import copy
from django.forms import Widget, TextInput


class Submit(TextInput):
    input_type = "submit"
    template_name = "widgets/submit.html"


class SubmitButtons(Widget):
    input_type = "submit"
    template_name = "widgets/submitSelect.html"
    option_template_name = "widgets/submitOption.html"
    option_inherits_attrs = False
    add_id_index = True
    selected_attribute = {}

    def __init__(self, choices=(), attrs=None, option_attrs=None, selected_class=None, inherit_attrs=False, *args, **kwargs):
        self.choices = tuple(choices)
        self.option_attrs = {} if option_attrs is None else option_attrs
        self.selected_class = selected_class
        self.option_inherits_attrs = inherit_attrs
        super().__init__(attrs)

    def __deepcopy__(self, memo):
        obj = copy.copy(self)
        obj.attrs = self.attrs.copy()
        obj.option_attrs = copy.copy(self.option_attrs)
        obj.choices = copy.copy(self.choices)
        memo[id(self)] = obj
        return obj

    def subwidgets(self, name, value, attrs=None):
        value = self.format_value(value)
        yield from self.create_options(name, value, attrs)

    def create_options(self, name, value, attrs=None):
        options = []
        for index, (opt_value, opt_label) in enumerate(self.choices):
            selected = (str(opt_value) in value)
            option = self.create_option(name, opt_value, opt_label, selected, index, attrs=attrs)
            options.append(option)
        return options

    def create_option(self, name, value, label, selected, index, subindex=None, attrs=None):
        index = str(index) if subindex is None else "%s_%s" % (index, subindex)
        if attrs is None:
            attrs = {}
        option_attrs = self.build_attrs(self.attrs, attrs) if self.option_inherits_attrs else {}
        if 'id' in option_attrs:
            option_attrs['id'] = self.id_for_label(option_attrs['id'], index)
        option_attrs.update(self.option_attrs)
        if selected:
            option_attrs.update(self.selected_attribute)
            if self.selected_class:
                if "class" in option_attrs:
                    option_attrs["class"] += " " + self.selected_class
                else:
                    option_attrs["class"] = self.selected_class
        return {
            'name': name,
            'value': value,
            'label': label,
            'selected': selected,
            'index': index,
            'attrs': option_attrs,
            'type': self.input_type,
            'template_name': self.option_template_name,
        }

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget']['options'] = self.create_options(name, context['widget']['value'], attrs)
        context['wrap_label'] = False
        return context

    def id_for_label(self, id_, index='0'):
        if id_ and self.add_id_index:
            id_ = '%s_%s' % (id_, index)
        return id_

    def value_from_datadict(self, data, files, name):
        getter = data.get
        return getter(name)

    def format_value(self, value):
        if value is None:
            return []
        if not isinstance(value, (tuple, list)):
            value = [value]
        return [str(v) if v is not None else '' for v in value]

    def use_required_attribute(self, initial):
        return False


class SubmitChoices(SubmitButtons):

    input_type = "submit"
    template_name = ""
    option_template_name = "widgets/submit.html"
    option_inherits_attrs = False
    add_id_index = True
    selected_attribute = {'title': "activo"}
