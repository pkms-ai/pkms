use sea_orm::entity::prelude::*;
use super::_entities::contents::{ActiveModel, Entity};
pub type Contents = Entity;

impl ActiveModelBehavior for ActiveModel {
    // extend activemodel below (keep comment for generators)
}
