use crate::{
    extension::postgres::Type,
    sea_orm::{DbBackend, DeriveActiveEnum, EnumIter, Schema},
};
use loco_rs::schema::table_auto_tz;
use sea_orm_migration::{prelude::*, schema::*};

#[derive(DeriveMigrationName)]
pub struct Migration;

#[async_trait::async_trait]
impl MigrationTrait for Migration {
    async fn up(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        let schema = Schema::new(DbBackend::Postgres);
        manager
            .create_type(schema.create_enum_from_active_enum::<ContentType>())
            .await?;
        manager
            .create_table(
                table_auto_tz(Contents::Table)
                    .col(pk_auto(Contents::Id))
                    .col(uuid_uniq(Contents::Pid))
                    .col(string_null(Contents::Title))
                    .col(string_uniq(Contents::Url))
                    .col(
                        ColumnDef::new(Contents::ContentType)
                            .custom(Alias::new("content_type")) // Use the enum type name
                            .not_null()
                            .to_owned(),
                    )
                    .col(string_null(Contents::ImageUrl))
                    .col(text_null(Contents::Description))
                    .col(text_null(Contents::RawContent))
                    .col(text_null(Contents::Summary))
                    .col(json_binary_null(Contents::Metadata))
                    .to_owned(),
            )
            .await?;
        Ok(())
    }

    async fn down(&self, manager: &SchemaManager) -> Result<(), DbErr> {
        manager
            .drop_table(Table::drop().table(Contents::Table).to_owned())
            .await?;
        // Drop the enum type roles_name
        manager
            .drop_type(
                Type::drop()
                    .if_exists()
                    .name(ContentTypeEnum)
                    .restrict()
                    .to_owned(),
            )
            .await?;
        Ok(())
    }
}

#[derive(DeriveIden)]
enum Contents {
    Table,
    Id,
    Pid,
    Title,
    Url,
    ContentType,
    ImageUrl,
    Description,
    RawContent,
    Summary,
    Metadata,
}

#[derive(EnumIter, DeriveActiveEnum)]
#[sea_orm(rs_type = "String", db_type = "Enum", enum_name = "content_type")]
pub enum ContentType {
    #[sea_orm(string_value = "web_article")]
    WebArticle,
    #[sea_orm(string_value = "youtube_video")]
    YoutubeVideo,
    #[sea_orm(string_value = "publication")]
    Publication,
    #[sea_orm(string_value = "bookmark")]
    Bookmark,
    #[sea_orm(string_value = "unknown")] // Corrected typo here
    Unknown,
}
