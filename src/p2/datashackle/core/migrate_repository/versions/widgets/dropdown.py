# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

def upgrade(migrate_engine, data):
    # dropdown plan
    result = data.p2_plan.insert().execute(plan_identifier='p2_span_dropdown',
                             so_module='p2.datashackle.core.models.span.dropdown',
                             so_type='Dropdown')
    dropdown_plan_id = result.inserted_primary_key[0]
    
    # p2_span_dropdown -> p2_linkage
    result = data.p2_linkage.insert().execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.core.models.span.dropdown',
                             source_classname='Dropdown',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=data.cardinalities['n:1'],
                             shareable=False,
                             cascade='all'
                             )
    linkage_id = result.inserted_primary_key[0]
    

    #
    # Dropdown widget
    #
    
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=300,
                             width=400,
                             form_identifier=data.generate_random_identifier(),
                             form_name="dropdown",
                             fk_p2_plan=data.widget_plan_id)

    form_id = result.inserted_primary_key[0]
    
    data.helpers.create_relation_widget(data, form_id, 0, 0,
                                        labeltext="dropdown widget -> label properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=0,
                                        )
    data.helpers.create_relation_widget(data, form_id, 0, 20,
                                        labeltext="Linkage properties (dropdown widget -> dropdown span)",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_dropdown_linkage",
                                        plan_identifier="p2_span_dropdown",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the label
                                        tab_order=1,
                                        )
    data.helpers.create_relation_widget(data, form_id, 0, 80,
                                        labeltext="dropdown widget -> dropdown span properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_dropdown",
                                        plan_identifier="p2_span_dropdown",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"', # we are only interested in the relation span
                                        tab_order=2,
                                        )
    data.helpers.create_labeltext_widget(data, form_id, 0,150,
        labeltext="Tab order",
        field_identifier="tab_order",
        defaultvalue="0",
        label_width=220,
        text_width = 80,
        tab_order=3,
    )
    data.helpers.insert_save_button(data, form_id, tab_order=4)
    data.helpers.insert_reset_button(data, form_id, tab_order=5)


    # Property forms for dropdown widget

    result = data.p2_form.insert().execute(
                             active=True,
                             height=100,
                             width=400,
                             form_identifier=data.generate_random_identifier(),
                             form_name="properties_dropdown",
                             fk_p2_plan=dropdown_plan_id,
                             )
    form_id = result.inserted_primary_key[0]
     
    ## "filter clause"   
    #data.helpers.create_labeltext_widget(data, form_id, 0, 0,
    #                                     labeltext="Optional filter", field_identifier="filter_clause", defaultvalue="")
    #
    data.helpers.create_labeltext_widget(data, form_id, 0,0,
        labeltext="Plan used for populating dropdown",
        field_identifier="plan_identifier",
        defaultvalue="",
        label_width=220,
        text_width= 80,
        tab_order=0,
    )
    data.helpers.create_labeltext_widget(data, form_id, 0,20,
        labeltext="Attribute used for populating dropdown",
        field_identifier="attr_name",
        defaultvalue="",
        label_width=220,
        text_width = 80,
        tab_order=1,
    )
    data.helpers.create_checkbox_widget(data, form_id, 'Required', 0, 40, 'required', True, tab_order=2)

    # properties_dropdown_linkage form for plan p2_span_dropdown (only wrapper form)
    result = data.p2_form.insert().execute(
                             active=True,
                             height=45,
                             width=350,
                             form_identifier=data.generate_random_identifier(),
                             form_name="properties_dropdown_linkage",
                             fk_p2_plan=dropdown_plan_id,
                             )

    form_id = result.inserted_primary_key[0]
    
    data.helpers.create_relation_widget(data, form_id, 0, 0,
                                        labeltext="Linkage properties (dropdown span -> Linkage)",
                                        linkage_id=linkage_id,
                                        form_name="properties_dropdown_linkage",
                                        plan_identifier="p2_linkage",
                                        label_visible=False, # we don't want to display the label,
                                        tab_order=0,
                                        )

    
    # properties_dropdown_linkage form for plan p2_linkage
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                         height=40,
                         width=345,
                         form_identifier=data.generate_random_identifier(),
                         form_name="properties_dropdown_linkage",
                         fk_p2_plan=data.linkage_plan_id)
    form_id = result.inserted_primary_key[0]
    
    # add widgets
    data.helpers.create_labeltext_widget(data, form_id, 0, 0,
                                         labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=0)
    data.helpers.create_labeltext_widget(data, form_id, 0, 20,
                                         labeltext="Attribute name", field_identifier="attr_name", defaultvalue="", tab_order=1)

    #                    
    # Dropdown archetype.
    #
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier=data.generate_random_identifier(),
                          widget_type="dropdown",
                          css_style="position: absolute; top: 190px; left: 0px;",
                          fk_p2_form=data.archetype_form_id)
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    label_width = 95
    # Archetype span 1
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                         span_identifier=data.generate_random_identifier(),
                         span_name="label",
                         css_style="width:" + str(label_width) + "px;",
                         span_type="label",
                         span_value="Dropdown",
                         characteristic=None)
                         
    # Archetype span 2
    identifier = data.generate_random_identifier()
    result = data.p2_span.insert().execute(fk_p2_widget=last_inserted_widget_id,
                        span_identifier=identifier,
                        span_name="piggyback",
                        span_type="dropdown",
                        css_style="left:" + str(label_width) + "px; width: 95px;",
                        span_value="",
                        characteristic=None)
    id = data.generate_random_identifier()
    data.p2_linkage.insert().execute(
        id=id,
        attr_name="dummy_dropdown_archetype"
        )
    data.p2_span_dropdown.insert().execute(span_identifier=identifier,
        fk_p2_linkage=id, cardinality='1,1'
    )
    return data
