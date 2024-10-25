use db_service::{app::App, models::_entities::contents::Entity};
use insta::{assert_debug_snapshot, with_settings};
use loco_rs::testing;
use rstest::rstest;
use sea_orm::EntityTrait;
use serde_json;
use serial_test::serial;

// TODO: see how to dedup / extract this to app-local test utils
// not to framework, because that would require a runtime dep on insta
macro_rules! configure_insta {
    ($($expr:expr),*) => {
        let mut settings = insta::Settings::clone_current();
        settings.set_prepend_module_to_snapshot(false);
        settings.set_snapshot_suffix("contents_request");
        let _guard = settings.bind_to_scope();
    };
}

#[tokio::test]
#[serial]
async fn can_add_content() {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let payload = serde_json::json!({
            "pid": "00000000-0000-0000-0000-000000001234",
            "title": "loco",
            "url": "https://loco.com",
            "content_type": "web_article",
            "image_url": "https://loco.com/image.jpg",
            "description": "loco description",
            "raw_content": "loco raw content",
            "summary": "loco summary",
            "metadata": {
                "key1": "value1",
                "key2": "value2"
            }
        });

        let add_content_request = request.post("/contents").json(&payload).await;

        with_settings!({
            filters => {
                 let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                    combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                    combined_filters
            }
        }, {
            assert_debug_snapshot!(
            (add_content_request.status_code(), add_content_request.text())
        );
        });
    })
    .await;
}

#[tokio::test]
#[serial]
async fn can_list() {
    configure_insta!();
    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();
        let res = request.get("/contents").await;
        // assert_eq!(res.status_code(), 200);

        // you can assert content like this:
        // assert_eq!(res.text(), "content");
        assert_debug_snapshot!((res.status_code(), res.text()));
    })
    .await;
}

#[tokio::test]
#[serial]
async fn can_get_content() {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let get_content_request = request.get("/contents/1").await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                (get_content_request.status_code(), get_content_request.text())
            );
        });
    })
    .await;
}

#[tokio::test]
#[serial]
async fn can_update_content() {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let payload = serde_json::json!({
            "title": "Updated Title",
            "url": "https://updated-url.com",
            "content_type": "publication"
        });

        let update_content_request = request.post("/contents/1").json(&payload).await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                (update_content_request.status_code(), update_content_request.text())
            );
        });
    })
    .await;
}

#[tokio::test]
#[serial]
async fn can_delete_content() {
    configure_insta!();

    testing::request::<App, _, _>(|request, ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let count_before_delete = Entity::find().all(&ctx.db).await.unwrap().len();
        let delete_content_request = request.delete("/contents/1").await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                (delete_content_request.status_code(), delete_content_request.text())
            );
        });

        let count_after_delete = Entity::find().all(&ctx.db).await.unwrap().len();
        assert_eq!(count_after_delete, count_before_delete - 1);
    })
    .await;
}

#[rstest]
#[case("get_contents", serde_json::json!({}))]
#[case("get_contents_with_page_size", serde_json::json!({"page_size":"1"}))]
#[case("get_contents_with_size_and_page", serde_json::json!({"page":"2", "page_size": "5"}))]
#[case("get_contents_with_filters", serde_json::json!({"page":"1", "page_size": "2", "title": "%loco%"}))]
#[tokio::test]
#[serial]
async fn can_get_contents(#[case] test_name: &str, #[case] params: serde_json::Value) {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let contents = request.get("/contents").add_query_params(params).await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                test_name, (contents.status_code(), contents.text())
            );
        });
    })
    .await;
}

#[tokio::test]
#[serial]
async fn check_url_exists(request: &testing::Request<App>, url: &str) {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let payload = serde_json::json!({
            "url": "https://example.com",
        });

        let update_content_request = request.post("/contents/check_url").json(&payload).await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                (update_content_request.status_code(), update_content_request.text())
            );
        });
    })
    .await;
}

#[tokio::test]
#[serial]
async fn check_url_not_exists(request: &testing::Request<App>, url: &str) {
    configure_insta!();

    testing::request::<App, _, _>(|request, _ctx| async move {
        let boot = testing::boot_test::<App>().await.unwrap();
        testing::seed::<App>(&boot.app_context.db).await.unwrap();

        let payload = serde_json::json!({
            "url": "https://exmple111.com",
        });

        let update_content_request = request.post("/contents/check_url").json(&payload).await;

        with_settings!({
            filters => {
                let mut combined_filters = testing::CLEANUP_DATE.to_vec();
                combined_filters.extend(vec![(r#"\"id\\":\d+"#, r#""id\":ID"#)]);
                combined_filters
            }
        }, {
            assert_debug_snapshot!(
                (update_content_request.status_code(), update_content_request.text())
            );
        });
    })
    .await;
}

// add test for empty pid
//
