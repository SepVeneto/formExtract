def to_html(layout: list):
  html = '<el-row>'
  rules = []
  for row in layout:
    for col in row:
      rule, form_item = to_form_item(col)
      if rule:
        rules.append(rule)
      html += form_item
  html += '</el-row>'
  return html

def to_form_item(info: tuple):
  labelConfig, type = info
  action = '请选择' if type == 'select' else '请输入'
  item = None
  prop_name = labelConfig.get('prop', None)
  if prop_name:
    prop = 'formData.' + labelConfig['prop']
  if type == 'select':
    item = '<bc-select v-model="%s" :options="[]" />' % prop
  elif type == 'input':
    item = '<bc-input v-model="%s" />' % prop
  elif type == 'datetime':
    item = '<el-date-picker v-model="%s" type="datetime" />' % prop
  elif type == 'textarea':
    item = '<bc-input v-model="%s" type="textarea" />' % prop
  else:
    item = '<span>%s</span>' % labelConfig['label']
  item += '\n'

  rule = None
  if labelConfig['required']:
    rule = '{ required: true, message: %s }' % (action + labelConfig['label'])
  if prop_name:
    tag = '<el-form-item label="%s" prop="%s">\n' % (labelConfig['label'], prop_name)
  else:
    tag = '<el-form-item label="%s">\n' % (labelConfig['label'])
  return rule, tag + item + "</el-form-item>\n"