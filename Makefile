REGISTRY   := dfkozlov

GIT_REPO   := $$(basename -s .git `git config --get remote.origin.url`)
GIT_BRANCH := $$(if [ -n "$$BRANCH_NAME" ]; then echo "$$BRANCH_NAME"; else git rev-parse --abbrev-ref HEAD; fi)
GIT_BRANCH := $$(echo "${GIT_BRANCH}" | tr '[:upper:]' '[:lower:]')
GIT_SHA1   := $$(git rev-parse HEAD)
NAME       := ${REGISTRY}/${GIT_REPO}_${GIT_BRANCH}
IMG_HASHED := "${NAME}:${GIT_SHA1}"
IMG_LATEST := "${NAME}:latest"
DOCKER_CMD := docker


all: build push

	@echo "$@ finished!"

build:

	@echo "Build has started..."

	@echo "Build docker image..."
	${DOCKER_CMD} build -t ${IMG_HASHED} -t ${IMG_LATEST} .

	@echo "Build has finished!"

api-tests:
	cd ansible;
	ansible-playbook playbooks/api-tests.yml -e "image_name=${IMG_HASHED}"
	cd ../;

push:

	@echo "Push has started..."

	${DOCKER_CMD} push ${IMG_HASHED}
	${DOCKER_CMD} push ${IMG_LATEST}

	@echo "Push has finished!"

run:

	${DOCKER_CMD} pull ${IMG_LATEST}
	${DOCKER_CMD} run --name junction-2019 -it --rm -p 8081:8080 ${IMG_LATEST}

stop:

	${DOCKER_CMD} rm -f junction-2019
