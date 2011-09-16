# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from sqlalchemy.sql import select

mod = __import__('001_initial_schema')
p2_fieldtype = getattr(mod, 'p2_fieldtype')


def upgrade(migrate_engine, data):

    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=310,
                             width=310,
                             form_identifier=data.generate_random_identifier(),
                             form_name="labeltext",
                             fk_p2_plan=data.widget_plan_id)
    labeltext_form_id = result.inserted_primary_key[0]
    

    data.helpers.create_relation_widget(data, labeltext_form_id, 0, 0,
                                        labeltext="Labeltext widget -> label properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only in the label interested
                                        tab_order=0,
                                        )
    data.helpers.create_relation_widget(data, labeltext_form_id, 0, 25,
                                        labeltext="Labeltext widget -> alphanumeric properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_alphanumeric",
                                        plan_identifier="p2_span_alphanumeric",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the alphanumeric span
                                        tab_order=1,
                                        )
    data.helpers.create_labeltext_widget(data, labeltext_form_id, 0, 125, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=2)
    data.helpers.insert_save_button(data, labeltext_form_id, tab_order=3)
    data.helpers.insert_reset_button(data, labeltext_form_id, tab_order=4)
    

    # Properties label span            
    result = data.p2_form.insert().execute(active=True,
                         height=20,
                         width=200,
                         form_identifier=data.generate_random_identifier(),
                         form_name="properties_label",
                         fk_p2_plan=data.span_plan_id)
    properties_label_id = result.inserted_primary_key[0]
    
    data.helpers.create_checkbox_widget(data, properties_label_id, 'Label visible', 0, 0, 'visible', True, tab_order=0)
   

    # Properties alphanumeric span
    result = data.p2_form.insert().execute(active=True,
        height=100,
        width=302,
        form_identifier=data.generate_random_identifier(),
        form_name="properties_alphanumeric",
        fk_p2_plan=data.alphanumeric_span_plan_id
    )
    properties_alphanumeric_id = result.inserted_primary_key[0]


    data.helpers.create_labeltext_widget(data, properties_alphanumeric_id, 0, 0, 'Table field', 'field_identifier', None, tab_order=0)
    data.helpers.create_labeltext_widget(data, properties_alphanumeric_id, 0, 20, 'Mapped attribute', 'attr_name', None, tab_order=1)
    data.helpers.create_checkbox_widget(data, properties_alphanumeric_id, 'Multiline', 0, 40, 'multi_line', False, tab_order=2)
    data.helpers.create_checkbox_widget(data, properties_alphanumeric_id, 'Required', 0, 60, 'required', True, tab_order=3)

    data.helpers.create_dropdown_widget(
        data,
        properties_alphanumeric_id,
        0,
        80,
        label='Field type',
        foreignkeycol='fk_field_type',
        attr_name='field_type',
        target_plan='p2_fieldtype',
        target_attr_name='field_type',
        required=True,
        tab_order=4
        )

   
    #
    # Labeltext archetype.
    #
    # Archetype widget
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="labeltext",
                          fk_p2_form=data.archetype_form_id)
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    label_width = 95
    # Archetype widget: span 1
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=data.generate_random_identifier(),
                         span_name="label",
                         css_style="width:" + str(label_width) + "px;",
                         span_type="label",
                         span_value="Text",
                         characteristic=None)

    fk_field_type = select([p2_fieldtype.c.id], p2_fieldtype.c.field_type == 'textline').execute().scalar()  
                     
    # Archetype widget: span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=identifier,
                        span_name="piggyback",
                        span_type="alphanumeric",
                        css_style="left:" + str(label_width) + "px; width:" + str(label_width) + "px;",
                        span_value="",
                        characteristic="text")
    data.p2_span_alphanumeric.insert().execute(
        span_identifier=identifier,
        fk_field_type=fk_field_type,
        attr_name='dummy_labeltext_archetype',
        field_identifier='dummy_labeltext_archetype',
    )
    return data
