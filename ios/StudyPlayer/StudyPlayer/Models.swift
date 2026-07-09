import Foundation

struct LessonManifest: Codable, Identifiable, Hashable {
    let schemaVersion: Int
    let id: String
    let course: String
    let slug: String
    let title: String
    let language: String?
    let duration: Double?
    let createdAt: String?
    let audio: String
    let transcriptJson: String
    let transcriptMarkdown: String?
    let segmentsCount: Int?

    enum CodingKeys: String, CodingKey {
        case schemaVersion = "schema_version"
        case id
        case course
        case slug
        case title
        case language
        case duration
        case createdAt = "created_at"
        case audio
        case transcriptJson = "transcript_json"
        case transcriptMarkdown = "transcript_markdown"
        case segmentsCount = "segments_count"
    }
}

struct TranscriptPayload: Codable, Hashable {
    let language: String?
    let duration: Double?
    let segments: [TranscriptSegment]
}

struct TranscriptSegment: Codable, Identifiable, Hashable {
    let id: Int
    let start: Double
    let end: Double
    let text: String
}

struct StoredLesson: Identifiable, Hashable {
    let manifest: LessonManifest
    let directoryURL: URL
    let transcript: TranscriptPayload

    var id: String { manifest.id }
    var audioURL: URL { directoryURL.appendingPathComponent(manifest.audio) }
    var progressURL: URL { directoryURL.appendingPathComponent("progress.json") }
}

struct PlaybackProgress: Codable {
    var currentTime: Double
    var updatedAt: Date
}

extension Double {
    var studyTimestamp: String {
        let total = Int(self.rounded(.down))
        let hours = total / 3600
        let minutes = (total % 3600) / 60
        let seconds = total % 60
        if hours > 0 {
            return String(format: "%02d:%02d:%02d", hours, minutes, seconds)
        }
        return String(format: "%02d:%02d", minutes, seconds)
    }
}

