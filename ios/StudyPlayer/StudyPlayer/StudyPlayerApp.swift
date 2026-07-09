import SwiftUI

@main
struct StudyPlayerApp: App {
    @StateObject private var store = StudyStore()

    var body: some Scene {
        WindowGroup {
            ContentView()
                .environmentObject(store)
                .onOpenURL { url in
                    store.importPackage(from: url)
                }
        }
    }
}

