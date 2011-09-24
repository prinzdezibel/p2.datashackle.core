# -*- coding: utf-8 -*-

def upgrade(migrate_engine):
    mod = __import__('001_initial_schema')
    
    data = mod.upgradedataobj()
    data.p2_plan = getattr(mod, 'p2_plan')
    data.p2_form = getattr(mod, 'p2_form')
    data.p2_widget = getattr(mod, 'p2_widget')
    data.p2_span = getattr(mod, 'p2_span')
    data.p2_linkage = getattr(mod, 'p2_linkage')
    data.p2_span_relation = getattr(mod, 'p2_span_relation')
    data.p2_span_fileupload = getattr(mod, 'p2_span_fileupload')
    data.p2_span_action = getattr(mod, 'p2_span_action')
    data.p2_span_alphanumeric = getattr(mod, 'p2_span_alphanumeric')
    data.p2_span_checkbox = getattr(mod, 'p2_span_checkbox')
    data.p2_span_dropdown = getattr(mod, 'p2_span_dropdown')

    # --- ARCHETYPE FORM ---
    
    insStmt = data.p2_plan.insert()
    result = insStmt.execute(plan_identifier='p2_archetype',   
                             so_module='p2.datashackle.core.models.setobject_types',
                             so_type='p2_archetype')
    last_inserted_id = result.inserted_primary_key[0]
    data.archetype_plan_id = last_inserted_id
    
    insStmt = data.p2_form.insert()
    result = insStmt.execute(active=True,
                         height=300,
                         width=230,
                         form_identifier=data.generate_random_identifier(),
                         form_name="archetypes",
                         fk_p2_plan=last_inserted_id)
    last_inserted_id = result.inserted_primary_key[0]
    migrate_engine.data['archetype_form_id'] = last_inserted_id
    
    

    # --- INITIAL LINKAGES ---
    # Add initial linkages
    
    # plan -> default_form
    insStmt = data.p2_linkage.insert()
    result = insStmt.execute(
        id=data.generate_random_identifier(),
        attr_name='default_form',
        ref_type='object',
        ref_key=None,
        foreignkeycol='fk_default_form',
        source_module='p2.datashackle.core.models.plan',
        source_classname='Plan',
        target_classname='FormType',
        target_module='p2.datashackle.core.models.form',
        fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
        cascade='save-update, merge',
        post_update=True, #http://www.sqlalchemy.org/docs/05/mappers.html#rows-that-point-to-themselves-mutually-dependent-rows
        )
    
    # plan -> forms[fk]
    insStmt = data.p2_linkage.insert()
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='forms',
                             ref_type='dict',
                             ref_key='form_name',
                             foreignkeycol='fk_p2_plan',
                             source_module='p2.datashackle.core.models.plan',
                             source_classname='Plan',
                             target_classname='FormType',
                             target_module='p2.datashackle.core.models.form',
                             back_populates='plan',
                             fk_cardinality=migrate_engine.data['cardinalities']['1:n'],
                             cascade='save-update, merge')
    
    # plan -> forms[fk] (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='plan',
                             ref_type='object',
                             foreignkeycol='fk_p2_plan',
                             back_populates='forms',
                             source_module='p2.datashackle.core.models.form',
                             source_classname='FormType',
                             target_classname='Plan',
                             target_module='p2.datashackle.core.models.plan',
                             fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                             cascade='all')
                             
    # form -> widgets[fk]
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='widgets',
                             ref_type='dict',
                             foreignkeycol='fk_p2_form',
                             source_module='p2.datashackle.core.models.form',
                             source_classname='FormType',
                             target_classname='WidgetType',
                             target_module='p2.datashackle.core.models.widget.widget',
                             back_populates='form',
                             fk_cardinality=migrate_engine.data['cardinalities']['1:n'],
                             cascade='save-update, merge')
                             
    # widget[fk] -> form (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                              attr_name='form',
                              ref_type='object',
                              foreignkeycol='fk_p2_form',
                              source_module='p2.datashackle.core.models.widget.widget',
                              source_classname='WidgetType',
                              target_module='p2.datashackle.core.models.form',
                              target_classname='FormType',
                              fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                              back_populates='widgets',
                              cascade='save-update, merge')
    
    # widget -> spans[fk]
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='spans',
                             ref_type='dict',
                             ref_key='span_name',
                             foreignkeycol='fk_p2_widget',
                             source_module='p2.datashackle.core.models.widget.widget',
                             source_classname='WidgetType',
                             target_classname='SpanType',
                             target_module='p2.datashackle.core.models.span.span',
                             fk_cardinality=migrate_engine.data['cardinalities']['1:n'],
                             back_populates='widget',
                             cascade='all')
    migrate_engine.data['widget_span_linkage'] = result.inserted_primary_key[0] 

    # span[fk] -> widget (backref)
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='widget',
                             ref_type='object',
                             foreignkeycol='fk_p2_widget',
                             source_classname='SpanType',
                             source_module='p2.datashackle.core.models.span.span',
                             target_module='p2.datashackle.core.models.widget.widget',
                             target_classname='WidgetType',
                             fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                             back_populates='spans',
                             cascade='save-update, merge'
                             )

    # p2_span_relation -> p2_linkage
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.core.models.span.relation',
                             source_classname='Relation',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                             cascade='all'
                             )
    migrate_engine.data['span_relation2linkage'] = result.inserted_primary_key[0]
    
    # p2_span_fileupload -> p2_linkage
    result = insStmt.execute(id=data.generate_random_identifier(),
                             attr_name='linkage',
                             ref_type='object',
                             foreignkeycol='fk_p2_linkage',
                             source_module='p2.datashackle.core.models.span.fileupload',
                             source_classname='Fileupload',
                             target_classname='Linkage',
                             target_module='p2.datashackle.core.models.linkage',
                             fk_cardinality=migrate_engine.data['cardinalities']['n:1'],
                             cascade='all'
                             )
    migrate_engine.data['span_fileupload2linkage'] = result.inserted_primary_key[0]

def downgrade(migrate_engine):
    pass

