# This file is auto-generated from the current state of the database. Instead
# of editing this file, please use the migrations feature of Active Record to
# incrementally modify your database, and then regenerate this schema definition.
#
# This file is the source Rails uses to define your schema when running `bin/rails
# db:schema:load`. When creating a new database, `bin/rails db:schema:load` tends to
# be faster and is potentially less error prone than running all of your
# migrations from scratch. Old migrations may fail to apply correctly if those
# migrations use external dependencies or application code.
#
# It's strongly recommended that you check this file into your version control system.

ActiveRecord::Schema[8.0].define(version: 2024_11_18_095723) do
  create_table "panels", force: :cascade do |t|
    t.string "name", null: false
    t.string "experiment", null: false
    t.string "title", null: false
    t.integer "order", default: 0, null: false
    t.integer "mission", default: 1, null: false
    t.boolean "sc1", default: false, null: false
    t.boolean "sc2", default: false, null: false
    t.boolean "sc3", default: false, null: false
    t.boolean "sc4", default: false, null: false
    t.boolean "scM", default: false, null: false
    t.boolean "stage", default: false, null: false
    t.boolean "zeroes", default: false, null: false
    t.boolean "active", default: false, null: false
    t.datetime "created_at", null: false
    t.datetime "updated_at", null: false
  end
end
