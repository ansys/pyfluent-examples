style:
	@python -m pip install pre-commit
	@pre-commit run --all-files --show-diff-on-failure

docker-pull:
	@pip install docker
	@python .ci/pull_fluent_image.py

build-doc:
	@sudo rm -rf /home/ansys/.local/share/ansys_fluent_core/examples/*
	@pip install -r requirements/requirements_doc.txt --force-reinstall
	@xvfb-run make -C doc html
	@touch doc/_build/html/.nojekyll
	@echo "$(DOCS_CNAME)" >> doc/_build/html/CNAME
