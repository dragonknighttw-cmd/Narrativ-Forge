import React, { useState, useEffect } from 'react';
import {
  SafeAreaView,
  View,
  Text,
  TouchableOpacity,
  FlatList,
  StyleSheet,
  ActivityIndicator,
  Modal,
  TextInput,
  Alert,
  ScrollView,
  Share
} from 'react-native';
import { StatusBar } from 'expo-status-bar';
import { api } from './src/api';
import { Episode, ProductionJob } from './src/types';

export default function App() {
  const [activeTab, setActiveTab] = useState<'queue' | 'episodes' | 'review' | 'publish'>('episodes');
  const [episodes, setEpisodes] = useState<Episode[]>([]);
  const [jobs, setJobs] = useState<ProductionJob[]>([]);
  const [loading, setLoading] = useState<boolean>(true);
  const [selectedEpisode, setSelectedEpisode] = useState<Episode | null>(null);
  const [rejectModalVisible, setRejectModalVisible] = useState<boolean>(false);
  const [rejectReason, setRejectReason] = useState<string>('');

  const loadData = async () => {
    setLoading(true);
    const [epData, jobData] = await Promise.all([api.getEpisodes(), api.getJobs()]);
    setEpisodes(epData);
    setJobs(jobData);
    if (epData.length > 0 && !selectedEpisode) {
      setSelectedEpisode(epData[0]);
    }
    setLoading(false);
  };

  useEffect(() => {
    loadData();
    const interval = setInterval(() => {
      api.getJobs().then(setJobs);
    }, 6000);
    return () => clearInterval(interval);
  }, []);

  const handleApprove = async (ep: Episode) => {
    Alert.alert(
      'အတည်ပြုမည်လား (Approve Video)?',
      `"${ep.title}" ကို အတည်ပြုပြီး Google Drive သို့ Export ထုတ်ပေးပါမည်။`,
      [
        { text: 'မလုပ်ပါ (Cancel)', style: 'cancel' },
        {
          text: 'အတည်ပြုသည် (Approve)',
          onPress: async () => {
            await api.approveEpisode(ep.id);
            Alert.alert('အောင်မြင်ပါသည်', 'Video ကို Approve ပြုလုပ်ပြီး Google Drive သို့ စတင်တင်ပို့နေပါပြီ။');
            loadData();
          }
        }
      ]
    );
  };

  const handleReject = async () => {
    if (!selectedEpisode) return;
    await api.rejectEpisode(selectedEpisode.id, rejectReason);
    setRejectModalVisible(false);
    setRejectReason('');
    Alert.alert('ပြန်လည်ပြင်ဆင်ခိုင်းပြီးပါပြီ', 'အယ်ဒီတာအဖွဲ့ထံ ပြန်လည်ပြင်ဆင်ရန် အကြောင်းကြားပြီးပါပြီ။');
    loadData();
  };

  const handleShare = async (ep: Episode) => {
    const message = `${ep.myanmar_title || ep.title}\n\n${ep.synopsis || ''}\n\n${(ep.hashtags || []).join(' ')}`;
    await Share.share({ message });
  };

  return (
    <SafeAreaView style={styles.container}>
      <StatusBar style="light" />

      {/* Header */}
      <View style={styles.header}>
        <View>
          <Text style={styles.headerTitle}>🎬 NARRATIV FORGE</Text>
          <Text style={styles.headerSubtitle}>Burmese Short-Form Video Studio</Text>
        </View>
        <TouchableOpacity style={styles.refreshBtn} onPress={loadData}>
          <Text style={styles.refreshBtnText}>🔄</Text>
        </TouchableOpacity>
      </View>

      {/* Tabs */}
      <View style={styles.tabsRow}>
        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'episodes' && styles.activeTabItem]}
          onPress={() => setActiveTab('episodes')}
        >
          <Text style={[styles.tabText, activeTab === 'episodes' && styles.activeTabText]}>
            Episodes ({episodes.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'queue' && styles.activeTabItem]}
          onPress={() => setActiveTab('queue')}
        >
          <Text style={[styles.tabText, activeTab === 'queue' && styles.activeTabText]}>
            Queue ({jobs.length})
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'review' && styles.activeTabItem]}
          onPress={() => setActiveTab('review')}
        >
          <Text style={[styles.tabText, activeTab === 'review' && styles.activeTabText]}>
            Review (9:16)
          </Text>
        </TouchableOpacity>

        <TouchableOpacity
          style={[styles.tabItem, activeTab === 'publish' && styles.activeTabItem]}
          onPress={() => setActiveTab('publish')}
        >
          <Text style={[styles.tabText, activeTab === 'publish' && styles.activeTabText]}>
            Publishing
          </Text>
        </TouchableOpacity>
      </View>

      {/* Content */}
      {loading ? (
        <View style={styles.centerContainer}>
          <ActivityIndicator size="large" color="#3b82f6" />
          <Text style={styles.loadingText}>Loading Video Pipelines...</Text>
        </View>
      ) : (
        <View style={styles.body}>
          {/* TAB 1: EPISODES */}
          {activeTab === 'episodes' && (
            <FlatList
              data={episodes}
              keyExtractor={(item) => item.id}
              contentContainerStyle={{ padding: 16 }}
              renderItem={({ item }) => (
                <View style={styles.episodeCard}>
                  <View style={styles.badgeRow}>
                    <Text style={styles.publicId}>{item.public_id}</Text>
                    <View style={[styles.statusBadge, getStatusStyle(item.status)]}>
                      <Text style={styles.statusText}>{item.status.toUpperCase()}</Text>
                    </View>
                  </View>

                  <Text style={styles.episodeTitle}>{item.title}</Text>
                  <Text style={styles.episodeSynopsis} numberOfLines={2}>
                    {item.synopsis || 'Short-form vertical Burmese video project.'}
                  </Text>

                  <View style={styles.cardFooter}>
                    <Text style={styles.durationText}>⏱️ {item.target_duration_seconds}s (9:16)</Text>
                    <TouchableOpacity
                      style={styles.reviewButton}
                      onPress={() => {
                        setSelectedEpisode(item);
                        setActiveTab('review');
                      }}
                    >
                      <Text style={styles.reviewButtonText}>Review Video →</Text>
                    </TouchableOpacity>
                  </View>
                </View>
              )}
            />
          )}

          {/* TAB 2: QUEUE */}
          {activeTab === 'queue' && (
            <FlatList
              data={jobs}
              keyExtractor={(item) => item.id}
              contentContainerStyle={{ padding: 16 }}
              renderItem={({ item }) => (
                <View style={styles.jobCard}>
                  <Text style={styles.jobEpisodeTitle}>{item.episode_title}</Text>
                  <Text style={styles.jobStep}>Step: {item.step}</Text>
                  <Text style={styles.jobTask}>{item.current_task}</Text>

                  {/* Progress Bar */}
                  <View style={styles.progressContainer}>
                    <View style={[styles.progressBar, { width: `${item.progress}%` }]} />
                  </View>
                  <View style={styles.progressFooter}>
                    <Text style={styles.progressLabel}>{item.status}</Text>
                    <Text style={styles.progressPercent}>{item.progress}%</Text>
                  </View>
                </View>
              )}
            />
          )}

          {/* TAB 3: REVIEW (9:16 PREVIEW) */}
          {activeTab === 'review' && (
            <ScrollView contentContainerStyle={{ padding: 16, alignItems: 'center' }}>
              {selectedEpisode ? (
                <>
                  <Text style={styles.reviewHeading}>{selectedEpisode.title}</Text>

                  {/* 9:16 Vertical Video Mock/Player Frame */}
                  <View style={styles.verticalVideoBox}>
                    <Text style={styles.videoBadge}>9:16 Vertical Video</Text>
                    <Text style={styles.videoPlayIcon}>▶️</Text>
                    <View style={styles.subtitleOverlay}>
                      <Text style={styles.subtitleText}>
                        "မြန်မာဘာသာ အသံနှင့် စာတန်းထိုး အပြည့်အစုံ"
                      </Text>
                    </View>
                  </View>

                  {/* Review Actions */}
                  <View style={styles.actionButtonsRow}>
                    <TouchableOpacity
                      style={styles.approveButton}
                      onPress={() => handleApprove(selectedEpisode)}
                    >
                      <Text style={styles.actionBtnText}>✅ Approve & Export</Text>
                    </TouchableOpacity>

                    <TouchableOpacity
                      style={styles.rejectButton}
                      onPress={() => setRejectModalVisible(true)}
                    >
                      <Text style={styles.actionBtnText}>❌ Request Edit</Text>
                    </TouchableOpacity>
                  </View>
                </>
              ) : (
                <Text style={styles.emptyText}>Please select an episode to review.</Text>
              )}
            </ScrollView>
          )}

          {/* TAB 4: PUBLISHING */}
          {activeTab === 'publish' && (
            <ScrollView contentContainerStyle={{ padding: 16 }}>
              {selectedEpisode ? (
                <View style={styles.publishBox}>
                  <Text style={styles.publishTitle}>📢 Quick Publishing Package</Text>
                  <Text style={styles.fieldLabel}>Myanmar Title & Caption:</Text>
                  <View style={styles.codeBlock}>
                    <Text style={styles.codeText}>
                      {selectedEpisode.myanmar_title || selectedEpisode.title}
                    </Text>
                  </View>

                  <Text style={styles.fieldLabel}>Hashtags:</Text>
                  <View style={styles.codeBlock}>
                    <Text style={styles.hashtagText}>
                      {(selectedEpisode.hashtags || ['#MyanmarShorts', '#AIContent']).join(' ')}
                    </Text>
                  </View>

                  <TouchableOpacity
                    style={styles.shareButton}
                    onPress={() => handleShare(selectedEpisode)}
                  >
                    <Text style={styles.shareButtonText}>📲 Share to TikTok / Reels / Shorts</Text>
                  </TouchableOpacity>
                </View>
              ) : (
                <Text style={styles.emptyText}>Select an episode first.</Text>
              )}
            </ScrollView>
          )}
        </View>
      )}

      {/* Reject Modal */}
      <Modal visible={rejectModalVisible} transparent animationType="fade">
        <View style={styles.modalOverlay}>
          <View style={styles.modalContent}>
            <Text style={styles.modalTitle}>ပြန်လည်ပြင်ဆင်ရန် အကြောင်းအရာ</Text>
            <TextInput
              style={styles.modalInput}
              placeholder="ဥပမာ- စာတန်းထိုးအချိန် ညှိရန်၊ အသံကျယ်ရန်..."
              placeholderTextColor="#71717a"
              multiline
              numberOfLines={4}
              value={rejectReason}
              onChangeText={setRejectReason}
            />
            <View style={styles.modalActions}>
              <TouchableOpacity
                style={styles.cancelBtn}
                onPress={() => setRejectModalVisible(false)}
              >
                <Text style={styles.cancelBtnText}>မလုပ်ပါ</Text>
              </TouchableOpacity>
              <TouchableOpacity style={styles.confirmRejectBtn} onPress={handleReject}>
                <Text style={styles.confirmBtnText}>အတည်ပြုသည်</Text>
              </TouchableOpacity>
            </View>
          </View>
        </View>
      </Modal>
    </SafeAreaView>
  );
}

function getStatusStyle(status: string) {
  switch (status) {
    case 'needs_approval':
      return { backgroundColor: '#f59e0b' };
    case 'approved':
    case 'exported':
      return { backgroundColor: '#10b981' };
    case 'processing':
    case 'in_production':
      return { backgroundColor: '#3b82f6' };
    case 'rejected':
    case 'failed':
      return { backgroundColor: '#ef4444' };
    default:
      return { backgroundColor: '#64748b' };
  }
}

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: '#09090b' },
  header: {
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#27272a',
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center'
  },
  headerTitle: { color: '#fafafa', fontSize: 18, fontWeight: 'bold', letterSpacing: 1 },
  headerSubtitle: { color: '#a1a1aa', fontSize: 11, marginTop: 2 },
  refreshBtn: { padding: 8, backgroundColor: '#18181b', borderRadius: 8 },
  refreshBtnText: { fontSize: 16 },
  tabsRow: {
    flexDirection: 'row',
    backgroundColor: '#18181b',
    borderBottomWidth: 1,
    borderBottomColor: '#27272a'
  },
  tabItem: { flex: 1, paddingVertical: 12, alignItems: 'center' },
  activeTabItem: { borderBottomWidth: 2, borderBottomColor: '#3b82f6' },
  tabText: { color: '#71717a', fontSize: 12, fontWeight: '600' },
  activeTabText: { color: '#3b82f6' },
  body: { flex: 1 },
  centerContainer: { flex: 1, justifyContent: 'center', alignItems: 'center' },
  loadingText: { color: '#a1a1aa', marginTop: 12, fontSize: 13 },
  episodeCard: {
    backgroundColor: '#18181b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#27272a'
  },
  badgeRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'center' },
  publicId: { color: '#3b82f6', fontSize: 12, fontWeight: 'bold' },
  statusBadge: { paddingHorizontal: 8, paddingVertical: 4, borderRadius: 6 },
  statusText: { color: '#09090b', fontSize: 10, fontWeight: 'bold' },
  episodeTitle: { color: '#fafafa', fontSize: 16, fontWeight: 'bold', marginTop: 8 },
  episodeSynopsis: { color: '#a1a1aa', fontSize: 13, marginTop: 4, lineHeight: 18 },
  cardFooter: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginTop: 14,
    borderTopWidth: 1,
    borderTopColor: '#27272a',
    paddingTop: 10
  },
  durationText: { color: '#71717a', fontSize: 12 },
  reviewButton: { backgroundColor: '#3b82f6', paddingHorizontal: 12, paddingVertical: 6, borderRadius: 6 },
  reviewButtonText: { color: '#ffffff', fontSize: 12, fontWeight: '600' },
  jobCard: {
    backgroundColor: '#18181b',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12,
    borderWidth: 1,
    borderColor: '#27272a'
  },
  jobEpisodeTitle: { color: '#fafafa', fontSize: 15, fontWeight: 'bold' },
  jobStep: { color: '#3b82f6', fontSize: 13, marginTop: 4, fontWeight: '600' },
  jobTask: { color: '#a1a1aa', fontSize: 12, marginTop: 2 },
  progressContainer: {
    height: 8,
    backgroundColor: '#27272a',
    borderRadius: 4,
    marginTop: 12,
    overflow: 'hidden'
  },
  progressBar: { height: '100%', backgroundColor: '#3b82f6' },
  progressFooter: { flexDirection: 'row', justifyContent: 'space-between', marginTop: 6 },
  progressLabel: { color: '#71717a', fontSize: 11, textTransform: 'capitalize' },
  progressPercent: { color: '#fafafa', fontSize: 11, fontWeight: 'bold' },
  reviewHeading: { color: '#fafafa', fontSize: 17, fontWeight: 'bold', marginBottom: 16, textAlign: 'center' },
  verticalVideoBox: {
    width: 225,
    height: 400,
    backgroundColor: '#000000',
    borderRadius: 16,
    borderWidth: 2,
    borderColor: '#3b82f6',
    justifyContent: 'center',
    alignItems: 'center',
    position: 'relative'
  },
  videoBadge: { position: 'absolute', top: 12, color: '#a1a1aa', fontSize: 11 },
  videoPlayIcon: { fontSize: 44 },
  subtitleOverlay: {
    position: 'absolute',
    bottom: 24,
    backgroundColor: 'rgba(0,0,0,0.7)',
    paddingHorizontal: 10,
    paddingVertical: 6,
    borderRadius: 6
  },
  subtitleText: { color: '#fef08a', fontSize: 12, fontWeight: 'bold', textAlign: 'center' },
  actionButtonsRow: { flexDirection: 'row', gap: 12, marginTop: 24 },
  approveButton: { backgroundColor: '#10b981', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 8 },
  rejectButton: { backgroundColor: '#ef4444', paddingVertical: 12, paddingHorizontal: 20, borderRadius: 8 },
  actionBtnText: { color: '#ffffff', fontWeight: 'bold', fontSize: 13 },
  emptyText: { color: '#71717a', fontSize: 14, marginTop: 40 },
  publishBox: { backgroundColor: '#18181b', borderRadius: 12, padding: 16, borderWidth: 1, borderColor: '#27272a' },
  publishTitle: { color: '#fafafa', fontSize: 16, fontWeight: 'bold', marginBottom: 12 },
  fieldLabel: { color: '#a1a1aa', fontSize: 12, marginTop: 10, marginBottom: 4 },
  codeBlock: { backgroundColor: '#09090b', padding: 12, borderRadius: 8, borderWidth: 1, borderColor: '#27272a' },
  codeText: { color: '#fafafa', fontSize: 14, lineHeight: 20 },
  hashtagText: { color: '#38bdf8', fontSize: 13 },
  shareButton: {
    backgroundColor: '#8b5cf6',
    paddingVertical: 14,
    borderRadius: 8,
    alignItems: 'center',
    marginTop: 20
  },
  shareButtonText: { color: '#ffffff', fontWeight: 'bold', fontSize: 14 },
  modalOverlay: { flex: 1, backgroundColor: 'rgba(0,0,0,0.7)', justifyContent: 'center', padding: 20 },
  modalContent: { backgroundColor: '#18181b', borderRadius: 12, padding: 20, borderWidth: 1, borderColor: '#27272a' },
  modalTitle: { color: '#fafafa', fontSize: 16, fontWeight: 'bold', marginBottom: 12 },
  modalInput: {
    backgroundColor: '#09090b',
    borderRadius: 8,
    color: '#fafafa',
    padding: 12,
    borderWidth: 1,
    borderColor: '#27272a',
    textAlignVertical: 'top'
  },
  modalActions: { flexDirection: 'row', justifyContent: 'flex-end', gap: 12, marginTop: 16 },
  cancelBtn: { paddingVertical: 8, paddingHorizontal: 16 },
  cancelBtnText: { color: '#a1a1aa', fontSize: 13 },
  confirmRejectBtn: { backgroundColor: '#ef4444', paddingVertical: 8, paddingHorizontal: 16, borderRadius: 6 },
  confirmBtnText: { color: '#ffffff', fontWeight: 'bold', fontSize: 13 }
});
