from orator.migrations import Migration


class CreatePasswordResetTable(Migration):

    def up(self):
        """
        Run the migrations.
        """
        with self.schema.create('password_reset') as table:
            table.increments('id')
            table.integer('user_id').unsigned()
            table.string('token')
            table.boolean('active')
            table.timestamps()

            table.foreign('user_id').references('id').on('users')

    def down(self):
        """
        Revert the migrations.
        """
        self.schema.drop('password_reset')
