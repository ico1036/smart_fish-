from app.models.project import Project, ProjectStatus, Ontology, EntityType, EdgeType, UploadedFile

def test_project_creation():
    p = Project(name="test")
    assert p.status == ProjectStatus.CREATED
    assert p.project_id is not None
    assert len(p.project_id) == 8

def test_project_status_transitions():
    p = Project(name="test")
    p.status = ProjectStatus.ONTOLOGY_GENERATED
    assert p.status == ProjectStatus.ONTOLOGY_GENERATED

def test_uploaded_file():
    f = UploadedFile(filename="test.pdf", size=1024)
    assert f.text_content == ""

def test_ontology():
    o = Ontology(
        entity_types=[EntityType(name="Person", description="A person")],
        edge_types=[EdgeType(name="KNOWS", description="Knows relationship")],
        analysis_summary="Test summary"
    )
    assert len(o.entity_types) == 1
    assert o.entity_types[0].name == "Person"
