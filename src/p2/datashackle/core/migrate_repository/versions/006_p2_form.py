# -*- coding: utf-8 -*-

mod = __import__('001_initial_schema')
p2_plan = getattr(mod, 'p2_plan')
p2_form = getattr(mod, 'p2_form')

def upgrade(migrate_engine):
    insStmt = p2_form.insert()
    result = insStmt.execute(active=True,
                             height=40,
                             width=410,
                             form_identifier=migrate_engine.generate_random_identifier(),
                             form_name="plans",
                             fk_p2_plan='p2_plan')
    migrate_engine.data['p2_plan_form_id'] = result.inserted_primary_key[0]
    p2_plan.update().where(p2_plan.c.plan_identifier == 'p2_plan').\
        execute(fk_default_form=migrate_engine.data['p2_plan_form_id']) 


def downgrade(migrate_engine):
    pass
