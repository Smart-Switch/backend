from orator.migrations import Migration


class CreateDevicesTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('devices') as table:
            table.increments('id')
            table.string('name').unique()
            table.string('topic')
            table.integer('user_id').unsigned()
            table.boolean('status').default(False)
            table.timestamps()

            table.foreign('user_id').references('id').on('users')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('devices')
