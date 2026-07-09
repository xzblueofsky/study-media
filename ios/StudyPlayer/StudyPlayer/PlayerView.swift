import AVFoundation
import SwiftUI

@MainActor
final class PlayerModel: ObservableObject {
    let lesson: StoredLesson
    let player: AVPlayer
    @Published var currentTime: Double = 0
    @Published var duration: Double = 0
    @Published var isPlaying = false
    @Published var activeSegmentID: Int?

    private var timeObserver: Any?
    private weak var store: StudyStore?

    init(lesson: StoredLesson, store: StudyStore) {
        self.lesson = lesson
        self.store = store
        self.player = AVPlayer(url: lesson.audioURL)
        self.currentTime = store.progress(for: lesson)
        self.duration = lesson.manifest.duration ?? lesson.transcript.duration ?? 0
        configureAudioSession()
        addTimeObserver()
        if currentTime > 0 {
            seek(to: currentTime, autoPlay: false)
        }
    }

    deinit {
        if let timeObserver {
            player.removeTimeObserver(timeObserver)
        }
    }

    func togglePlay() {
        if isPlaying {
            player.pause()
            isPlaying = false
            saveProgress()
        } else {
            player.play()
            isPlaying = true
        }
    }

    func seek(to seconds: Double, autoPlay: Bool = true) {
        let time = CMTime(seconds: seconds, preferredTimescale: 600)
        player.seek(to: time, toleranceBefore: .zero, toleranceAfter: .zero)
        currentTime = seconds
        updateActiveSegment()
        if autoPlay {
            player.play()
            isPlaying = true
        }
    }

    func seekFromSlider(to seconds: Double) {
        seek(to: seconds, autoPlay: isPlaying)
    }

    func saveProgress() {
        store?.saveProgress(currentTime, for: lesson)
    }

    private func configureAudioSession() {
        do {
            try AVAudioSession.sharedInstance().setCategory(.playback, mode: .spokenAudio)
            try AVAudioSession.sharedInstance().setActive(true)
        } catch {
            // Playback still works in most foreground cases; keep the UI usable.
        }
    }

    private func addTimeObserver() {
        let interval = CMTime(seconds: 0.35, preferredTimescale: 600)
        timeObserver = player.addPeriodicTimeObserver(forInterval: interval, queue: .main) { [weak self] time in
            guard let self else { return }
            self.currentTime = time.seconds
            if let itemDuration = self.player.currentItem?.duration.seconds,
               itemDuration.isFinite,
               itemDuration > 0 {
                self.duration = itemDuration
            }
            self.updateActiveSegment()
        }
    }

    private func updateActiveSegment() {
        activeSegmentID = lesson.transcript.segments.last { segment in
            currentTime >= segment.start && currentTime < segment.end
        }?.id
    }
}

struct PlayerView: View {
    let lesson: StoredLesson
    @EnvironmentObject private var store: StudyStore
    @StateObject private var model: PlayerModel
    @State private var sliderValue: Double = 0
    @State private var isEditingSlider = false

    init(lesson: StoredLesson, store: StudyStore) {
        self.lesson = lesson
        _model = StateObject(wrappedValue: PlayerModel(lesson: lesson, store: store))
    }

    var body: some View {
        VStack(spacing: 0) {
            controls
            Divider()
            transcript
        }
        .navigationTitle(lesson.manifest.title)
        .navigationBarTitleDisplayMode(.inline)
        .onChange(of: model.currentTime) { _, newValue in
            if !isEditingSlider {
                sliderValue = newValue
            }
        }
        .onDisappear {
            model.saveProgress()
        }
    }

    private var controls: some View {
        VStack(alignment: .leading, spacing: 10) {
            Text(lesson.manifest.course)
                .font(.subheadline)
                .foregroundStyle(.secondary)
            HStack {
                Button {
                    model.togglePlay()
                } label: {
                    Label(model.isPlaying ? "暂停" : "播放", systemImage: model.isPlaying ? "pause.fill" : "play.fill")
                }
                .buttonStyle(.borderedProminent)

                Text(model.currentTime.studyTimestamp)
                    .font(.system(.body, design: .monospaced))
                Spacer()
                Text(max(model.duration, model.currentTime).studyTimestamp)
                    .font(.system(.body, design: .monospaced))
                    .foregroundStyle(.secondary)
            }

            Slider(
                value: $sliderValue,
                in: 0...max(model.duration, 1),
                onEditingChanged: { editing in
                    isEditingSlider = editing
                    if !editing {
                        model.seekFromSlider(to: sliderValue)
                    }
                }
            )
        }
        .padding()
        .background(.bar)
    }

    private var transcript: some View {
        ScrollViewReader { proxy in
            ScrollView {
                LazyVStack(alignment: .leading, spacing: 0) {
                    ForEach(lesson.transcript.segments) { segment in
                        Button {
                            model.seek(to: segment.start)
                        } label: {
                            HStack(alignment: .top, spacing: 12) {
                                Text(segment.start.studyTimestamp)
                                    .font(.system(.subheadline, design: .monospaced))
                                    .foregroundStyle(.teal)
                                    .frame(width: 72, alignment: .leading)
                                Text(segment.text)
                                    .font(.body)
                                    .foregroundStyle(.primary)
                                    .frame(maxWidth: .infinity, alignment: .leading)
                            }
                            .padding(.vertical, 10)
                            .padding(.horizontal)
                            .contentShape(Rectangle())
                            .background(segment.id == model.activeSegmentID ? Color.teal.opacity(0.13) : Color.clear)
                        }
                        .buttonStyle(.plain)
                        .id(segment.id)
                        Divider()
                            .padding(.leading, 100)
                    }
                }
            }
            .onChange(of: model.activeSegmentID) { _, segmentID in
                guard let segmentID else { return }
                withAnimation(.easeOut(duration: 0.25)) {
                    proxy.scrollTo(segmentID, anchor: .center)
                }
            }
        }
    }
}

