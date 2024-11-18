class CreatePanels < ActiveRecord::Migration[8.0]
  def change
    create_table :panels do |t|
      t.string :name, null: false
      t.string :experiment, null: false
      t.string :title, null: false
      t.integer :order, null: false, default: 0
      t.integer :mission, null: false, default: 1
      t.boolean :sc1, null: false, default: false
      t.boolean :sc2, null: false, default: false
      t.boolean :sc3, null: false, default: false
      t.boolean :sc4, null: false, default: false
      t.boolean :scM, null: false, default: false
      t.boolean :stage, null: false, default: false
      t.boolean :zeroes, null: false, default: false
      t.boolean :active, null: false, default: false

      t.timestamps
    end
  end
end
