# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

def upgrade(migrate_engine, data):
    
    # Checkbox properties
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=310,
                             width=310,
                             form_identifier=data.generate_random_identifier(),
                             form_name="checkbox",
                             fk_p2_plan=data.widget_plan_id)
    form_id = result.inserted_primary_key[0]
    

    data.helpers.create_relation_widget(data, form_id, 0, 0,
                                        labeltext="Checkbox widget -> label properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only in the label interested
                                        tab_order=0,
                                        )
    data.helpers.create_relation_widget(data, form_id, 0, 25,
                                        labeltext="Checkbox widget -> checkbox properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_checkbox",
                                        plan_identifier="p2_span_checkbox",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the checkbox span
                                        tab_order=1,
                                        )
    data.helpers.create_labeltext_widget(data, form_id, 0, 65, 'Tab order', 'tab_order', None, tab_order=2)
    data.helpers.insert_save_button(data, form_id, tab_order=3)
    data.helpers.insert_reset_button(data, form_id, tab_order=4)
    
   

    # Properties checkbox span
    result = data.p2_form.insert().execute(active=True,
                         height=40,
                         width=302,
                         form_identifier=data.generate_random_identifier(),
                         form_name="properties_checkbox",
                         fk_p2_plan=data.checkbox_span_plan_id)
    form_id = result.inserted_primary_key[0]

    data.helpers.create_labeltext_widget(data, form_id, 0, 0, 'Table field', 'field_identifier', None, tab_order=0)
    data.helpers.create_labeltext_widget(data, form_id, 0, 20, 'Mapped attribute', 'attr_name', None, tab_order=1)

    # END LABELTEXT PROPERTIES #
    
    # Checkbox archetype.
    #
    # Archetype widget
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier='09087262',
                          widget_type="checkbox",
                          css_style="position: absolute; top: 30px; left: 0px;",
                          fk_p2_form=data.archetype_form_id)
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    label_width = 95
    # Archetype widget: span 1
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier='62256862',
                            span_name="label",
                            css_style="width:" + str(label_width) + "px;",
                            span_type="label",
                            span_value="Checkbox",
                            characteristic=None)
                            
    # Archetype widget: span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=identifier,
                            span_name="piggyback",
                            span_type="checkbox",
                            css_style="left:" + str(label_width) + "px;",
                            span_value=None,
                            characteristic=None)
    data.p2_span_checkbox.insert().execute(span_identifier=identifier)
    
    return data
