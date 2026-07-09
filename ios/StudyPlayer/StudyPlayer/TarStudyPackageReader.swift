import Foundation

enum StudyPackageError: LocalizedError {
    case invalidArchive
    case missingEntry(String)
    case unsupportedSchema(Int)
    case unsafeManifestId(String)

    var errorDescription: String? {
        switch self {
        case .invalidArchive:
            return "学习包格式无效。"
        case .missingEntry(let name):
            return "学习包缺少文件：\(name)"
        case .unsupportedSchema(let version):
            return "不支持的学习包版本：\(version)"
        case .unsafeManifestId(let id):
            return "学习包 ID 不安全：\(id)"
        }
    }
}

struct StudyPackageArchive {
    let entries: [String: Data]

    func data(named name: String) throws -> Data {
        guard let data = entries[name] else {
            throw StudyPackageError.missingEntry(name)
        }
        return data
    }
}

enum TarStudyPackageReader {
    static func read(url: URL) throws -> StudyPackageArchive {
        let data = try Data(contentsOf: url)
        var offset = 0
        var entries: [String: Data] = [:]

        while offset + 512 <= data.count {
            let header = data.subdata(in: offset..<(offset + 512))
            if header.allSatisfy({ $0 == 0 }) {
                break
            }

            guard let name = stringField(header, start: 0, length: 100), !name.isEmpty else {
                throw StudyPackageError.invalidArchive
            }
            let prefix = stringField(header, start: 345, length: 155) ?? ""
            let fullName = prefix.isEmpty ? name : "\(prefix)/\(name)"
            let size = octalField(header, start: 124, length: 12)
            let typeFlag = header[156]
            let dataStart = offset + 512
            let dataEnd = dataStart + size
            guard dataEnd <= data.count else {
                throw StudyPackageError.invalidArchive
            }

            if typeFlag == 0 || typeFlag == 48 {
                entries[fullName] = data.subdata(in: dataStart..<dataEnd)
            }

            let paddedSize = ((size + 511) / 512) * 512
            offset = dataStart + paddedSize
        }

        guard !entries.isEmpty else {
            throw StudyPackageError.invalidArchive
        }
        return StudyPackageArchive(entries: entries)
    }

    private static func stringField(_ data: Data, start: Int, length: Int) -> String? {
        let field = data.subdata(in: start..<(start + length))
        let bytes = Array(field.prefix { $0 != 0 })
        return String(bytes: bytes, encoding: .utf8)
    }

    private static func octalField(_ data: Data, start: Int, length: Int) -> Int {
        let field = data.subdata(in: start..<(start + length))
        let text = String(bytes: field.filter { $0 != 0 && $0 != 32 }, encoding: .ascii) ?? "0"
        return Int(text.trimmingCharacters(in: .whitespacesAndNewlines), radix: 8) ?? 0
    }
}

