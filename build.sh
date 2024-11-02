docker build --target production -t universal-worker -f ./services/universal_worker/Dockerfile ./services/universal_worker/

docker build --target production -t content-manager -f ./services/content-submission-service/Dockerfile ./services/content-submission-service/
