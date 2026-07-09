import SwiftUI
import UniformTypeIdentifiers

extension UTType {
    static let studyPackage = UTType(filenameExtension: "study") ?? .data
}

struct ContentView: View {
    @EnvironmentObject private var store: StudyStore
    @State private var importing = false
    @State private var selectedLesson: StoredLesson?

    var body: some View {
        NavigationStack {
            Group {
                if store.lessons.isEmpty {
                    ContentUnavailableView(
                        "还没有课程",
                        systemImage: "music.note.list",
                        description: Text("点击右上角导入 .study 学习包。")
                    )
                } else {
                    List {
                        ForEach(store.lessons) { lesson in
                            NavigationLink {
                                PlayerView(lesson: lesson, store: store)
                            } label: {
                                VStack(alignment: .leading, spacing: 4) {
                                    Text(lesson.manifest.title)
                                        .font(.headline)
                                    Text(lesson.manifest.course)
                                        .font(.subheadline)
                                        .foregroundStyle(.secondary)
                                    Text("\(lesson.transcript.segments.count) 段")
                                        .font(.caption)
                                        .foregroundStyle(.secondary)
                                }
                            }
                        }
                        .onDelete { offsets in
                            for offset in offsets {
                                store.deleteLesson(store.lessons[offset])
                            }
                        }
                    }
                }
            }
            .navigationTitle("Study Player")
            .toolbar {
                ToolbarItem(placement: .topBarTrailing) {
                    Button {
                        importing = true
                    } label: {
                        Label("导入", systemImage: "square.and.arrow.down")
                    }
                }
            }
            .overlay {
                if store.isImporting {
                    ProgressView("正在导入")
                        .padding()
                        .background(.regularMaterial, in: RoundedRectangle(cornerRadius: 10))
                }
            }
            .fileImporter(
                isPresented: $importing,
                allowedContentTypes: [.studyPackage],
                allowsMultipleSelection: false
            ) { result in
                switch result {
                case .success(let urls):
                    guard let url = urls.first else { return }
                    store.importPackage(from: url)
                case .failure(let error):
                    store.message = "选择文件失败：\(error.localizedDescription)"
                }
            }
            .alert("提示", isPresented: Binding(
                get: { store.message != nil },
                set: { if !$0 { store.message = nil } }
            )) {
                Button("好") {
                    store.message = nil
                }
            } message: {
                Text(store.message ?? "")
            }
        }
        .onAppear {
            store.loadLibrary()
        }
    }
}

