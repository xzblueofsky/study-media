import Foundation
import SwiftUI

@MainActor
final class StudyStore: ObservableObject {
    @Published private(set) var lessons: [StoredLesson] = []
    @Published var isImporting = false
    @Published var message: String?

    private let decoder = JSONDecoder()
    private let encoder = JSONEncoder()

    init() {
        encoder.outputFormatting = [.prettyPrinted, .sortedKeys]
    }

    var lessonsRootURL: URL {
        let documents = FileManager.default.urls(for: .documentDirectory, in: .userDomainMask)[0]
        return documents.appendingPathComponent("Lessons", isDirectory: true)
    }

    func loadLibrary() {
        do {
            try FileManager.default.createDirectory(at: lessonsRootURL, withIntermediateDirectories: true)
            let lessonDirs = try FileManager.default.contentsOfDirectory(
                at: lessonsRootURL,
                includingPropertiesForKeys: [.isDirectoryKey],
                options: [.skipsHiddenFiles]
            )
            var loaded: [StoredLesson] = []
            for dir in lessonDirs {
                guard (try? dir.resourceValues(forKeys: [.isDirectoryKey]).isDirectory) == true else {
                    continue
                }
                let manifestURL = dir.appendingPathComponent("manifest.json")
                let transcriptURL = dir.appendingPathComponent("transcript.json")
                guard FileManager.default.fileExists(atPath: manifestURL.path),
                      FileManager.default.fileExists(atPath: transcriptURL.path) else {
                    continue
                }
                let manifest = try decoder.decode(LessonManifest.self, from: Data(contentsOf: manifestURL))
                let transcript = try decoder.decode(TranscriptPayload.self, from: Data(contentsOf: transcriptURL))
                loaded.append(StoredLesson(manifest: manifest, directoryURL: dir, transcript: transcript))
            }
            lessons = loaded.sorted { lhs, rhs in
                if lhs.manifest.course == rhs.manifest.course {
                    return lhs.manifest.title < rhs.manifest.title
                }
                return lhs.manifest.course < rhs.manifest.course
            }
        } catch {
            message = "读取课程库失败：\(error.localizedDescription)"
        }
    }

    func importPackage(from url: URL) {
        isImporting = true
        defer { isImporting = false }

        let hasAccess = url.startAccessingSecurityScopedResource()
        defer {
            if hasAccess {
                url.stopAccessingSecurityScopedResource()
            }
        }

        do {
            let archive = try TarStudyPackageReader.read(url: url)
            let manifest = try decoder.decode(LessonManifest.self, from: archive.data(named: "manifest.json"))
            guard manifest.schemaVersion == 1 else {
                throw StudyPackageError.unsupportedSchema(manifest.schemaVersion)
            }
            let safeID = safeDirectoryName(for: manifest.id)
            guard !safeID.isEmpty else {
                throw StudyPackageError.unsafeManifestId(manifest.id)
            }

            let destination = lessonsRootURL.appendingPathComponent(safeID, isDirectory: true)
            try FileManager.default.createDirectory(at: lessonsRootURL, withIntermediateDirectories: true)
            if FileManager.default.fileExists(atPath: destination.path) {
                try FileManager.default.removeItem(at: destination)
            }
            try FileManager.default.createDirectory(at: destination, withIntermediateDirectories: true)

            try archive.data(named: "manifest.json").write(to: destination.appendingPathComponent("manifest.json"))
            try archive.data(named: manifest.audio).write(to: destination.appendingPathComponent(manifest.audio))
            try archive.data(named: manifest.transcriptJson).write(to: destination.appendingPathComponent(manifest.transcriptJson))
            if let markdown = manifest.transcriptMarkdown,
               let markdownData = archive.entries[markdown] {
                try markdownData.write(to: destination.appendingPathComponent(markdown))
            }

            loadLibrary()
            message = "已导入：\(manifest.title)"
        } catch {
            message = "导入失败：\(error.localizedDescription)"
        }
    }

    func deleteLesson(_ lesson: StoredLesson) {
        do {
            try FileManager.default.removeItem(at: lesson.directoryURL)
            loadLibrary()
        } catch {
            message = "删除失败：\(error.localizedDescription)"
        }
    }

    func progress(for lesson: StoredLesson) -> Double {
        guard let data = try? Data(contentsOf: lesson.progressURL),
              let progress = try? decoder.decode(PlaybackProgress.self, from: data) else {
            return 0
        }
        return progress.currentTime
    }

    func saveProgress(_ time: Double, for lesson: StoredLesson) {
        let progress = PlaybackProgress(currentTime: time, updatedAt: Date())
        guard let data = try? encoder.encode(progress) else {
            return
        }
        try? data.write(to: lesson.progressURL)
    }

    private func safeDirectoryName(for id: String) -> String {
        let allowed = CharacterSet.alphanumerics.union(CharacterSet(charactersIn: "-_."))
        return id.unicodeScalars.map { scalar in
            allowed.contains(scalar) ? String(scalar) : "-"
        }.joined()
    }
}

