# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

def upgrade(migrate_engine, data):
    

    # --- RELATION ---

    #
    # Relation widget
    #
    
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=300,
                             width=400,
                             form_identifier=data.generate_random_identifier(),
                             form_name="relation",
                             fk_p2_plan=data.widget_plan_id)

    form_id = result.inserted_primary_key[0]
    
    data.helpers.create_relation_widget(data, form_id, 0, 0,
                                        labeltext="target form wrapper",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="target_form",
                                        plan_identifier="p2_span_relation",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the relation span
                                        tab_order=0,
                                        )
    data.helpers.create_relation_widget(data, form_id, 0, 40,
                                        labeltext="Linkage properties (Relation widget -> relation span)",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_linkage",
                                        plan_identifier="p2_span_relation",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the label
                                        tab_order=1,
                                        )
    data.helpers.create_relation_widget(data, form_id, 0, 140,
        labeltext="Labeltext widget -> relation span properties",
        linkage_id=data.widget_span_linkage,
        form_name="properties_relation",
        plan_identifier="p2_span_relation",
        label_visible=False, # we don't want to display the label,
        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the relation span
        tab_order=2,
        )
    data.helpers.create_relation_widget(data, form_id, 0, 220,
                                        labeltext="Labeltext widget -> label properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=3,
                                        )
    
    data.helpers.create_labeltext_widget(data, form_id, 0, 240, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=3)
    data.helpers.insert_save_button(data, form_id, tab_order=4)
    data.helpers.insert_reset_button(data, form_id, tab_order=5)



    # BEG target form form
    result = data.p2_form.insert().execute(
                             active=True,
                             height=40,
                             width=350,
                             form_identifier=data.generate_random_identifier(),
                             form_name="target_form",
                             fk_p2_plan=data.relation_span_plan_id,
                             )
    form_id = result.inserted_primary_key[0]
     
    # "plan_identifier" widget
    data.helpers.create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Plan used for display", field_identifier="plan_identifier", defaultvalue="", tab_order=0)
    
    # "form_name" widget
    data.helpers.create_labeltext_widget(data, form_id, 0, 20,
        labeltext="Used Form", field_identifier="form_name", defaultvalue="default_form", tab_order=1)
    
    # END target form form


    # properties_relation form
    result = data.p2_form.insert().execute(
                             active=True,
                             height=40,
                             width=350,
                             form_identifier=data.generate_random_identifier(),
                             form_name="properties_relation",
                             fk_p2_plan=data.relation_span_plan_id,
                             )
    form_id = result.inserted_primary_key[0]
     
    # "filter clause"   
    data.helpers.create_labeltext_widget(data, form_id, 0, 0,
        labeltext="Optional filter",
        field_identifier="filter_clause",
        defaultvalue="",
        tab_order=0,
        required=False
    )
    
    data.helpers.create_checkbox_widget(data,
                                        form_id,
                                        labeltext="Editable",
                                        x=0,
                                        y=20,
                                        field_identifier="editable",
                                        span_value=True,
                                        tab_order=3,
                                        )


    # properties_linkage form (only wrapper form for p2_relation_span)
    result = data.p2_form.insert().execute(
                             active=True,
                             height=140,
                             width=350,
                             form_identifier=data.generate_random_identifier(),
                             form_name="properties_linkage",
                             fk_p2_plan=data.relation_span_plan_id,
                             )

    form_id = result.inserted_primary_key[0]
    
    data.helpers.create_relation_widget(data, form_id, 0, 0,
                                        labeltext="Linkage properties (Relation span -> Linkage)",
                                        linkage_id=data.span_relation2linkage,
                                        form_name="properties_linkage",
                                        plan_identifier="p2_linkage",
                                        label_visible=False, # we don't want to display the label,
                                        tab_order=1,
                                        )

    # properties_linkage form
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                         height=100,
                         width=345,
                         form_identifier=data.generate_random_identifier(),
                         form_name="properties_linkage",
                         fk_p2_plan=data.linkage_plan_id)
    form_id = result.inserted_primary_key[0]
    
    data.helpers.create_dropdown_widget(
        data,
        form_id,
        0,
        0,
        'Cardinality',
        'fk_cardinality',
        'cardinality',
        'p2_cardinality',
        'cardinality',
        False,
        tab_order=0
    )

    data.helpers.create_labeltext_widget(data, form_id, 0, 20,
                                         labeltext="Mapping attribute", field_identifier="attr_name", defaultvalue="", tab_order=1)
    data.helpers.create_labeltext_widget(data, form_id, 0, 40,
                                         labeltext="xref table name", field_identifier="xref_table", defaultvalue="", tab_order=2, required=False)

    data.helpers.create_labeltext_widget(data, form_id, 0, 60,
                                         labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=3)
    data.helpers.create_labeltext_widget(data, form_id, 0, 80,
                                         labeltext="Second foreign key", field_identifier="foreignkeycol2", defaultvalue="", tab_order=4, required=False)
 
    #                    
    # Relation archetype.
    #
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="relation",
                          css_style="position: absolute; top: 130px; left: 0px;",
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
                         span_value="Relation",
                         characteristic=None)
                         
    # Archetype widget: span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=identifier,
                        span_name="piggyback",
                        span_type="relation",
                        css_style="left:" + str(label_width) + "px; width: 50px; height:50px;",
                        span_value="",
                        characteristic=None)
    id = data.generate_random_identifier()
    data.p2_linkage.insert().execute(
        id=id,
        attr_name="dummy_relation_archetype"
    )
    data.p2_span_relation.insert().execute(span_identifier=identifier,
        fk_p2_linkage=id, cardinality='1,1'
    )
    return data
