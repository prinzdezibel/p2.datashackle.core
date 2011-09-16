# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

from sqlalchemy.sql import select, and_


mod = __import__('001_initial_schema')
p2_widget = getattr(mod, 'p2_widget')
p2_span = getattr(mod, 'p2_span')
p2_span_alphanumeric = getattr(mod, 'p2_span_alphanumeric')
p2_span_checkbox = getattr(mod, 'p2_span_checkbox')
p2_span_relation = getattr(mod, 'p2_span_relation')
p2_span_action = getattr(mod, 'p2_span_action')
p2_span_dropdown = getattr(mod, 'p2_span_dropdown')
p2_linkage = getattr(mod, 'p2_linkage')
p2_form = getattr(mod, 'p2_form')
p2_plan = getattr(mod, 'p2_plan')
p2_fieldtype = getattr(mod, 'p2_fieldtype')


def create_labeltext_widget(data,
        form_id,
        xpos,
        ypos,
        labeltext,
        field_identifier,
        defaultvalue,
        tab_order,
        label_width=150,
        text_width=150,
        required=True
    ):
    # widget
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                             widget_type="labeltext",
                             css_style="position: absolute; top: " + str(ypos) + "px; left: " + str(xpos) + "px;",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]

    # span 1
    insStmt = p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=data.generate_random_identifier(),
                             span_name="label",
                             span_type="label",
                             css_style="width: " + str(label_width) + "px;",
                             span_value=labeltext,
                             )
    # span 2
    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="piggyback",
                             span_type="alphanumeric",
                             span_value=defaultvalue,
                             tab_order=tab_order,
                             css_style="left:" + str(label_width) + "px; width:" + str(text_width) + "px;",
                             )

    fk_field_type = select([p2_fieldtype.c.id], p2_fieldtype.c.field_type == 'textline').execute().scalar()

    result = p2_span_alphanumeric.insert().execute(
        span_identifier=span_identifier,
        field_identifier=field_identifier,
        attr_name=field_identifier,
        fk_field_type=fk_field_type,
        required=required,
        )
    return data # not really needed, but to stay consistent with the other functions


    
def insert_save_button(data, form_id, tab_order):
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="action",
                          css_style="position: absolute; top: 270px; left: 0px;",
                          fk_p2_form=form_id,
                          tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    insStmt = p2_span.insert()
    span_identifier = data.generate_random_identifier()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="button",
                         span_type="action",
                         span_value="OK",
                         css_style="width:60px",
                         ) 
    p2_span_action.insert().execute(span_identifier=span_identifier,
                                         msg_reset=False,
                                         msg_close=True
                                         )
        
        
                 

def insert_reset_button(data, form_id, tab_order):    
    # Insert Reset Action widget into form
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="action",
                          css_style="position: absolute; top: 270px; left: 105px",
                          fk_p2_form=form_id,
                          tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]
    # Button span
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=span_identifier,
                         span_name="button",
                         span_type="action",
                         span_value="Reset",
                         css_style="width:60px",
                         )
    p2_span_action.insert().execute(span_identifier=span_identifier,
                                         msg_reset=True,
                                         msg_close=False
                                         )
 
    

def create_relation_widget(data, form_id, xpos, ypos, labeltext, linkage_id, form_name,
                            plan_identifier, tab_order, filter_clause=None, label_visible=True):
    # widget
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                             widget_type="relation",
                             css_style="position: absolute; top: " + str(ypos) + "px; left: " + str(xpos) + "px;",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]


    # span 1
    if label_visible:
        label_width = 150
    else:
        label_width = 0 # Don't use up space for label

    insStmt = p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=data.generate_random_identifier(),
                             span_name="label",
                             span_type="label",
                             css_style="width: " + str(label_width) + "px;",
                             span_value=labeltext,
                             visible=label_visible
                             )
    # span 2
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                             span_identifier=span_identifier,
                             span_name="piggyback",
                             span_type="relation",
                             css_style="left:" + str(label_width) + "px;",
                             span_value=None,
                             visible=True
                            )
    p2_span_relation.insert().execute(
                                    span_identifier=span_identifier,
                                    fk_p2_linkage=linkage_id,
                                    form_name=form_name,
                                    label_visible=True,
                                    plan_identifier=plan_identifier,
                                    filter_clause=filter_clause,
                                    editable=False
                                    )
    return data # not really needed, but to stay consistent with the other functions


def create_checkbox_widget(data, form_id, labeltext, x, y, field_identifier, span_value, tab_order):
    
    label_width = 150
    
    insStmt = p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                             widget_type="checkbox",
                             css_style="position: absolute; top: " + str(y) + "px; left: " + str(x) + "px;",
                             fk_p2_form=form_id,
                             tab_order=tab_order)
    last_inserted_widget_id = result.inserted_primary_key[0]

    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=data.generate_random_identifier(),
                           span_name="label",
                           span_type="label",
                           css_style="width: " + str(label_width) + "px;",
                           span_value=labeltext,
                           )                           
    span_identifier = data.generate_random_identifier()
    result = p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=span_identifier,
                           #field_identifier=field_identifier,
                           span_name="piggyback",
                           css_style="left:" + str(label_width) + "px;",
                           span_type="checkbox",
                           span_value=span_value,
                           )
    result = p2_span_checkbox.insert().execute(
        span_identifier=span_identifier,
        field_identifier=field_identifier,
        attr_name=field_identifier
        ) 

def create_dropdown_widget(
        data,
        form_id,
        x,
        y,
        label,
        foreignkeycol,
        attr_name,
        target_plan,
        target_attr_name,
        required,
        tab_order
    ):
    (source_classname, source_module) = select([p2_plan.c.so_type, p2_plan.c.so_module],
            and_(p2_form.c.fk_p2_plan == p2_plan.c.plan_identifier, p2_form.c.form_identifier == form_id)
        ).execute().fetchone()
    (target_classname, target_module) = select([p2_plan.c.so_type, p2_plan.c.so_module],
        p2_plan.c.plan_identifier == target_plan).execute().fetchone()
    label_width = 150
    result = p2_widget.insert().execute(
        widget_identifier=data.generate_random_identifier(),
        widget_type="dropdown",
        css_style="position: absolute; top: " + str(y) + "px; left: " + str(x) + "px;",
        fk_p2_form=form_id,
        tab_order=tab_order
    )
    last_inserted_widget_id = result.inserted_primary_key[0]
    result = p2_span.insert().execute(
        fk_p2_widget=last_inserted_widget_id,
        span_identifier=data.generate_random_identifier(),
        span_name="label",
        span_type="label",
        css_style="width: " + str(label_width) + "px;",
        span_value=label,
    )                           

    linkage_id = data.generate_random_identifier()
    result = p2_linkage.insert().execute(
        id=linkage_id,
        attr_name=attr_name,
        ref_type='object',
        ref_key=None,
        foreignkeycol=foreignkeycol,
        source_module=source_module,
        source_classname=source_classname,
        target_module=target_module,
        target_classname=target_classname,
        back_populates = None,
        fk_cardinality=data.cardinalities['n:1'],
        cascade='save-update,merge',
        post_update=None,
    )

    span_identifier = data.generate_random_identifier()
    p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                           span_identifier=span_identifier,
                           span_name="piggyback",
                           css_style="left:" + str(label_width) + "px; width: 150px;",
                           span_type="dropdown",
                           )
    result = p2_span_dropdown.insert().execute(
        span_identifier=span_identifier,
        fk_p2_linkage=linkage_id,
        plan_identifier=target_plan,
        attr_name=target_attr_name,
        required=required,
   ) 

