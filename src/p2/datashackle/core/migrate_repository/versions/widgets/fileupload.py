# -*- coding: utf-8 -*-
# Copyright (C) projekt-und-partner.com, 2011
# Author:  Jonas Thiem <jonas.thiem%40projekt-und-partner.com>

def upgrade(migrate_engine, data):

    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                             height=320,
                             width=400,
                             form_identifier="63161474",
                             form_name="fileupload",
                             fk_p2_plan=data.widget_plan_id)
    propertyform_id = result.inserted_primary_key[0]
    
    data.helpers.create_relation_widget(data, propertyform_id, 0, 0,
                                        labeltext="Fileupload widget -> label properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_label",
                                        plan_identifier="p2_span",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="label"', # we are only interested in the label
                                        tab_order=0,
                                        )
    
    data.helpers.create_relation_widget(data, propertyform_id, 0, 20,
                                        labeltext="Fileupload widget -> fileupload span properties",
                                        linkage_id=data.widget_span_linkage,
                                        form_name="properties_fileupload",
                                        plan_identifier="p2_span_fileupload",
                                        label_visible=False, # we don't want to display the label,
                                        filter_clause='p2_span.span_name="piggyback"',
                                        tab_order=1,
                                        )
    data.helpers.create_labeltext_widget(data, propertyform_id, 0, 65, labeltext="Tab order", field_identifier="tab_order", defaultvalue="0", tab_order=2)
    
    # properties_linkage form:
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                         height=80,
                         width=345,
                         form_identifier=data.generate_random_identifier(),
                         form_name="properties_linkage_fileupload",
                         fk_p2_plan=data.linkage_plan_id)
    form_id = result.inserted_primary_key[0]
    
    # add widgets
    data.helpers.create_labeltext_widget(data, form_id, 0, 0,
                                         labeltext="Mapping attribute", field_identifier="attr_name", defaultvalue="", tab_order=0)
    data.helpers.create_labeltext_widget(data, form_id, 0, 20,
                                         labeltext="Foreign key name", field_identifier="foreignkeycol", defaultvalue="", tab_order=1)
    
    
    # properties_fileupload form
    result = data.p2_form.insert().execute(
                             active=True,
                             height=125,
                             width=350,
                             form_identifier=data.generate_random_identifier(),
                             form_name="properties_fileupload",
                             fk_p2_plan=data.fileupload_span_plan_id,
                             )
    form_id = result.inserted_primary_key[0]

    data.helpers.create_relation_widget(data, form_id, 0, 0,
                             labeltext="Linkage properties (Relation span -> Linkage)",
                             linkage_id=data.span_fileupload2linkage,
                             form_name="properties_linkage_fileupload",
                             plan_identifier="p2_linkage",
                             label_visible=False, # we don't want to display the label,
                             tab_order=0,
                             )
    
    data.helpers.insert_save_button(data, propertyform_id, tab_order=3)
    data.helpers.insert_reset_button(data, propertyform_id, tab_order=4)
    

    #                    
    # Fileupload widget for archetype form
    #
    insStmt = data.p2_widget.insert()
    result = insStmt.execute(widget_identifier='09087162',
                          widget_type="fileupload",
                          css_style="position: absolute; top: 60px; left: 0px;",
                          fk_p2_form=data.archetype_form_id)
    last_inserted_widget_id = result.inserted_primary_key[0]
    
    # Span 1 for Fileupload widget
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier='62256812',
                            span_name="label",
                            span_type="label",
                            span_value="Fileupload",
                            css_style="width: 60px;",
                            characteristic=None)
    # Span 2 for Fileupload widget
    identifier = data.generate_random_identifier()
    insStmt = data.p2_span.insert()
    result = insStmt.execute(fk_p2_widget=last_inserted_widget_id,
                            span_identifier=identifier,
                            span_name="piggyback",
                            span_type="fileupload",
                            css_style="left: 95px; width:50px; height:50px;",
                            span_value=None,
                            characteristic=None)
    data.p2_span_fileupload.insert().execute(span_identifier=identifier)
    return data
