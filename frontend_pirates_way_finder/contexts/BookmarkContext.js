import React, { createContext, useContext, useState, useEffect } from 'react';
import AsyncStorage from '@react-native-async-storage/async-storage';

const BookmarkContext = createContext();

const BOOKMARKS_STORAGE_KEY = '@pirateswayfinder:bookmarks';

export function BookmarkProvider({ children }) {
  const [bookmarkedNodes, setBookmarkedNodes] = useState(new Set());
  const [loading, setLoading] = useState(true);

  // Load bookmarks from AsyncStorage on mount
  useEffect(() => {
    loadBookmarks();
  }, []);

  const loadBookmarks = async () => {
    try {
      const saved = await AsyncStorage.getItem(BOOKMARKS_STORAGE_KEY);
      if (saved) {
        const bookmarksArray = JSON.parse(saved);
        setBookmarkedNodes(new Set(bookmarksArray));
        console.log(`📚 Loaded ${bookmarksArray.length} bookmarks from storage`);
      }
    } catch (error) {
      console.error('❌ Error loading bookmarks:', error);
    } finally {
      setLoading(false);
    }
  };

  const saveBookmarks = async (bookmarks) => {
    try {
      const bookmarksArray = Array.from(bookmarks);
      await AsyncStorage.setItem(BOOKMARKS_STORAGE_KEY, JSON.stringify(bookmarksArray));
      console.log(`💾 Saved ${bookmarksArray.length} bookmarks to storage`);
    } catch (error) {
      console.error('❌ Error saving bookmarks:', error);
    }
  };

  const addBookmark = (nodeId) => {
    const newBookmarks = new Set(bookmarkedNodes);
    newBookmarks.add(nodeId);
    setBookmarkedNodes(newBookmarks);
    saveBookmarks(newBookmarks);
    console.log(`❤️ Added bookmark: ${nodeId}`);
  };

  const removeBookmark = (nodeId) => {
    const newBookmarks = new Set(bookmarkedNodes);
    newBookmarks.delete(nodeId);
    setBookmarkedNodes(newBookmarks);
    saveBookmarks(newBookmarks);
    console.log(`💔 Removed bookmark: ${nodeId}`);
  };

  const toggleBookmark = (node) => {
    const nodeId = node?.properties?.id || node?.id;
    if (!nodeId) {
      console.error('❌ Cannot bookmark: no node ID');
      return;
    }

    if (bookmarkedNodes.has(nodeId)) {
      removeBookmark(nodeId);
    } else {
      addBookmark(nodeId);
    }
  };

  const isBookmarked = (node) => {
    const nodeId = node?.properties?.id || node?.id;
    return bookmarkedNodes.has(nodeId);
  };

  const getBookmarkedNodeIds = () => {
    return Array.from(bookmarkedNodes);
  };

  const value = {
    bookmarkedNodes,
    isBookmarked,
    toggleBookmark,
    addBookmark,
    removeBookmark,
    getBookmarkedNodeIds,
    loading,
  };

  return (
    <BookmarkContext.Provider value={value}>
      {children}
    </BookmarkContext.Provider>
  );
}

export function useBookmarks() {
  const context = useContext(BookmarkContext);
  if (!context) {
    throw new Error('useBookmarks must be used within a BookmarkProvider');
  }
  return context;
}

