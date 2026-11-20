import os
import pymupdf

DOCS_FOLDER = "./base"
os.makedirs(DOCS_FOLDER, exist_ok=True)

pdf_documents = {
    "vanguard_architecture.pdf": (
        "Project Vanguard_1 Architecture Overview\n\n"
        "Vanguard_1 is a cross-platform desktop application built on Electron. "
        "It uses SQLite for local persistent storage, React for UI components, "
        "and Tailwind CSS for styling. The key feature is real-time data synchronization "
        "across multiple client devices."
    ),
    "mirage_ml_pipeline.pdf": (
        "Project Mirage_2 Machine Learning Pipeline\n\n"
        "Mirage_2 is an automated ML pipeline implemented in Python. "
        "It relies on scikit-learn for model training, pytest for automated unit testing, "
        "and FastAPI to expose low-latency REST endpoints with real-time data synchronization."
    ),
    "flux_golang_service.pdf": (
        "Project Flux_7 High-Load Microservice\n\n"
        "Flux_7 is a backend microservice written in Go (Golang). "
        "It integrates Redis for distributed caching, Prometheus for metrics collection, "
        "and gRPC for high-speed inter-service communication complying with enterprise standards."
    ),
    "aspnet_backend_guide.pdf": (
        "ASP.NET Core Backend Architecture\n\n"
        "Enterprise backend API service built with ASP.NET Core and Entity Framework Core, "
        "featuring JWT authentication, role-based access control (RBAC), "
        "and PostgreSQL database integration deployed via Docker."
    )
}

for filename, content in pdf_documents.items():
    file_path = os.path.join(DOCS_FOLDER, filename)
    doc = pymupdf.open()
    page = doc.new_page()
    rect = pymupdf.Rect(50, 50, 545, 790)
    page.insert_textbox(rect, content, fontsize=12, fontname="helv")
    doc.save(file_path)
    doc.close()
    print(f"[OK] Created: {file_path}")

print("\nБазу PDF-документів успішно створено!")