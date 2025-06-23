// Global variables to store analysis results and ID
let currentAnalysisResult = null;
let currentAnalysisId = null;
let imagesPaths = {};
// Base URL for API requests
const API_BASE_URL = 'http://127.0.0.1:3000';

document.addEventListener('DOMContentLoaded', function() {
    // Add event listeners
    document.getElementById('analyzeBtn').addEventListener('click', analyzeText);
    document.getElementById('loadSampleBtn').addEventListener('click', loadSampleText);
    document.getElementById('convertBtn').addEventListener('click', convertText);
    document.getElementById('copyBtn').addEventListener('click', copyResultText);
    document.getElementById('downloadBtn').addEventListener('click', downloadConvertedText);
    
    // Downloads
    document.getElementById('downloadBasicVisualizationsBtn').addEventListener('click', downloadBasicVisualizations);
    document.getElementById('downloadAdvancedVisualizationsBtn').addEventListener('click', downloadAdvancedVisualizations);
    document.getElementById('downloadDataAsJson').addEventListener('click', downloadDataAsJson);
    document.getElementById('downloadDataAsCsv').addEventListener('click', downloadDataAsCsv);
    document.getElementById('downloadEverythingBtn').addEventListener('click', downloadEverything);
    document.getElementById('downloadAllVisualizationsBtn').addEventListener('click', downloadAllVisualizations);
    
    // New advanced features
    document.getElementById('similarityAnalyzeBtn').addEventListener('click', analyzeSimilarity);
    document.getElementById('loadSimilarityExampleBtn').addEventListener('click', loadSimilarityExample);
    document.getElementById('uploadFileBtn').addEventListener('click', uploadAndParseFile);
    document.getElementById('checkCapabilitiesBtn').addEventListener('click', checkSystemCapabilities);
    document.getElementById('analyzeFileContentBtn').addEventListener('click', analyzeFileContent);
    document.getElementById('generateInteractiveVizBtn').addEventListener('click', generateInteractiveVisualizations);
    
    // Add click handlers for all visualization images to show in modal
    document.querySelectorAll('.viz-img').forEach(img => {
        img.addEventListener('click', function() {
            showImageInModal(this.src, this.alt);
        });
    });
    
    // Add click handlers for download links
    document.querySelectorAll('.download-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const vizType = this.dataset.viz;
            if (imagesPaths[vizType]) {
                downloadImage(imagesPaths[vizType], `${vizType}.png`);
            }
        });
    });
});

function analyzeText() {
    const text = document.getElementById('analyzeText').value.trim();
    if (!text) {
        alert('請輸入要分析的文本');
        return;
    }
    
    // Reset interactive visualizations when starting new analysis
    resetInteractiveVisualizations();
    
    // Show loading indicator
    document.getElementById('loadingIndicator').classList.remove('d-none');
    document.getElementById('emptyState').classList.add('d-none');
    document.getElementById('analysisResults').classList.add('d-none');
    
    // Send request to analyze API
    fetch(`${API_BASE_URL}/api/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ text: text }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('分析請求失敗');
        }
        return response.json();
    })
    .then(data => {
        // Store results globally
        currentAnalysisResult = data;
        
        // Extract analysis ID from visualization paths
        if (data.visualizations && data.visualizations.wordcloud) {
            const path = data.visualizations.wordcloud;
            const matches = path.match(/\/static\/results\/([^\/]+)/);
            if (matches && matches[1]) {
                currentAnalysisId = matches[1];
            }
        }
        
        // Update UI with results
        displayAnalysisResults(data);
        
        // If report generation is enabled, start generating it
        if (document.getElementById('generateReportSwitch').checked) {
            generateReport();
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('分析失敗: ' + error.message);
    })
    .finally(() => {
        // Hide loading indicator
        document.getElementById('loadingIndicator').classList.add('d-none');
    });
}

function displayAnalysisResults(data) {
    // Store image paths for download links
    imagesPaths = data.visualizations || {};
    
    // Hide empty state and show results
    document.getElementById('emptyState').classList.add('d-none');
    document.getElementById('analysisResults').classList.remove('d-none');
    
    // Set images for basic visualizations
    if (data.visualizations) {
        // Basic visualizations
        updateVisualizationImage('wordcloudImg', data.visualizations.wordcloud);
        updateVisualizationImage('wordFreqImg', data.visualizations.word_frequency);
        updateVisualizationImage('posDistImg', data.visualizations.pos_distribution);
        updateVisualizationImage('sentimentImg', data.visualizations.sentiment);
        updateVisualizationImage('entitiesImg', data.visualizations.entities);
        
        // Advanced visualizations
        updateVisualizationImage('wordFreqVerticalImg', data.visualizations.word_frequency_vertical);
        updateVisualizationImage('wordFreqPieImg', data.visualizations.word_frequency_pie);
        updateVisualizationImage('keywordsImg', data.visualizations.keywords);
        updateVisualizationImage('ngramsImg', data.visualizations.ngrams);
        updateVisualizationImage('wordLengthImg', data.visualizations.word_by_length);
    }
    
    // Update data tables
    updateDataTables(data);
    
    // Update statistics badges
    updateStatsBadges(data);
    
    // Show the generate interactive visualizations button
    document.getElementById('generateInteractiveVizBtn').classList.remove('d-none');
    
    // Auto-generate interactive visualizations if enabled
    if (document.getElementById('generateInteractiveVizSwitch') && 
        document.getElementById('generateInteractiveVizSwitch').checked) {
        setTimeout(() => {
            generateInteractiveVisualizations();
        }, 1000); // Delay to let the main analysis complete
    }
    
    // Update complete report previews
    updateCompleteReportPreviews();
}

function updateVisualizationImage(imgId, imgPath) {
    const imgElement = document.getElementById(imgId);
    if (imgElement && imgPath) {
        imgElement.src = imgPath;
        imgElement.classList.remove('d-none');
        
        // Add click handler for modal preview
        imgElement.addEventListener('click', function() {
            showImageInModal(imgPath, this.alt);
        });
        
        // Show the parent container
        let container = imgElement.closest('.viz-container');
        if (container) {
            container.classList.remove('d-none');
        }
    } else if (imgElement) {
        imgElement.classList.add('d-none');
        
        // Hide the parent container if the image is unavailable
        let container = imgElement.closest('.viz-container');
        if (container) {
            container.classList.add('d-none');
        }
    }
}

function updateDataTables(data) {
    // Word frequency table
    if (data.word_frequency) {
        const wordFreqContainer = document.getElementById('wordFrequencyList');
        wordFreqContainer.innerHTML = createFrequencyTable(data.word_frequency, 30);
    }
    
    // POS distribution table
    if (data.pos_distribution) {
        const posContainer = document.getElementById('posDistribution');
        posContainer.innerHTML = createFrequencyTable(data.pos_distribution, 20);
    }
    
    // Named entities
    if (data.entities) {
        const entitiesContainer = document.getElementById('namedEntities');
        entitiesContainer.innerHTML = createEntitiesList(data.entities);
    }
    
    // Sentiment analysis
    if (data.sentiment) {
        const sentimentContainer = document.getElementById('sentimentAnalysis');
        sentimentContainer.innerHTML = createSentimentDisplay(data.sentiment);
    }
    
    // Keywords list
    if (data.keywords) {
        const keywordsContainer = document.getElementById('keywordsList');
        keywordsContainer.innerHTML = createWeightedTable(data.keywords, 20);
    }
    
    // N-grams list
    if (data.ngrams) {
        const ngramsContainer = document.getElementById('ngramsList');
        ngramsContainer.innerHTML = createFrequencyTable(data.ngrams, 20);
    }
}

function updateStatsBadges(data) {
    // Update total words badge
    const totalWordsBadge = document.getElementById('totalWordsBadge');
    if (totalWordsBadge && data.total_words !== undefined) {
        totalWordsBadge.textContent = `總詞數: ${data.total_words}`;
    }
    
    // Update average word length badge
    const avgWordLengthBadge = document.getElementById('avgWordLengthBadge');
    if (avgWordLengthBadge && data.avg_word_length !== undefined) {
        avgWordLengthBadge.textContent = `平均詞長: ${data.avg_word_length}`;
    }
    
    // Update sentiment badge
    const sentimentBadge = document.getElementById('sentimentBadge');
    if (sentimentBadge && data.sentiment && data.sentiment.sentiment_label) {
        let sentimentText = '未知';
        let sentimentClass = '';
        
        switch (data.sentiment.sentiment_label) {
            case 'positive':
                sentimentText = '正面';
                sentimentClass = 'sentiment-positive';
                break;
            case 'negative':
                sentimentText = '負面';
                sentimentClass = 'sentiment-negative';
                break;
            case 'neutral':
                sentimentText = '中性';
                sentimentClass = 'sentiment-neutral';
                break;
        }
        
        sentimentBadge.textContent = `情感: ${sentimentText}`;
        sentimentBadge.className = 'badge rounded-pill ' + sentimentClass;
    }
}

function createFrequencyTable(data, limit = 20) {
    // Sort by frequency (descending)
    const sortedItems = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit);
    
    // Find the maximum frequency for scaling bars
    const maxFreq = sortedItems.length > 0 ? sortedItems[0][1] : 0;
    
    let html = `
    <table class="frequency-table">
        <thead>
            <tr>
                <th style="width: 50%">項目</th>
                <th>頻率</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    sortedItems.forEach(([item, freq]) => {
        const percentage = maxFreq > 0 ? (freq / maxFreq) * 100 : 0;
        
        html += `
        <tr>
            <td>${item}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="frequency-bar" style="width: ${percentage}%"></div>
                    <span class="frequency-number">${freq}</span>
                </div>
            </td>
        </tr>
        `;
    });
    
    html += `
        </tbody>
    </table>
    `;
    
    return html;
}

function createWeightedTable(data, limit = 20) {
    // Sort by weight (descending)
    const sortedItems = Object.entries(data)
        .sort((a, b) => b[1] - a[1])
        .slice(0, limit);
    
    // Find the maximum weight for scaling bars
    const maxWeight = sortedItems.length > 0 ? sortedItems[0][1] : 0;
    
    let html = `
    <table class="frequency-table">
        <thead>
            <tr>
                <th style="width: 50%">項目</th>
                <th>權重</th>
            </tr>
        </thead>
        <tbody>
    `;
    
    sortedItems.forEach(([item, weight]) => {
        const percentage = maxWeight > 0 ? (weight / maxWeight) * 100 : 0;
        
        html += `
        <tr>
            <td>${item}</td>
            <td>
                <div class="d-flex align-items-center">
                    <div class="frequency-bar" style="width: ${percentage}%"></div>
                    <span class="frequency-number">${weight.toFixed(3)}</span>
                </div>
            </td>
        </tr>
        `;
    });
    
    html += `
        </tbody>
    </table>
    `;
    
    return html;
}

function createEntitiesList(entities) {
    let html = '';
    
    // Map entity types to display names and CSS classes
    const entityTypesMap = {
        'person': { name: '人名', class: 'entity-person' },
        'location': { name: '地名', class: 'entity-location' },
        'organization': { name: '機構名', class: 'entity-organization' }
    };
    
    // Generate HTML for each entity type
    Object.entries(entities).forEach(([type, items]) => {
        if (items && items.length > 0) {
            const typeInfo = entityTypesMap[type] || { name: type, class: 'entity-other' };
            
            html += `<h6>${typeInfo.name} (${items.length})</h6><div>`;
            
            items.forEach(item => {
                html += `<span class="entity-tag ${typeInfo.class}">${item}</span>`;
            });
            
            html += `</div><hr>`;
        }
    });
    
    return html || '<p class="text-muted">未檢測到命名實體</p>';
}

function createSentimentDisplay(sentiment) {
    let sentimentClass = 'sentiment-neutral';
    let sentimentText = '中性';
    let sentimentIcon = 'bi-emoji-neutral';
    
    if (sentiment.sentiment_label === 'positive') {
        sentimentClass = 'sentiment-positive';
        sentimentText = '正面';
        sentimentIcon = 'bi-emoji-smile';
    } else if (sentiment.sentiment_label === 'negative') {
        sentimentClass = 'sentiment-negative';
        sentimentText = '負面';
        sentimentIcon = 'bi-emoji-frown';
    }
    
    let html = `
    <div class="text-center mb-4">
        <i class="bi ${sentimentIcon} ${sentimentClass}" style="font-size: 3rem;"></i>
        <h4 class="${sentimentClass} mt-2">${sentimentText}</h4>
    </div>
    
    <div class="row mt-3">
        <div class="col-6">
            <div class="card bg-light">
                <div class="card-body text-center">
                    <h5 class="sentiment-positive">正面詞數</h5>
                    <h2>${sentiment.positive_count}</h2>
                </div>
            </div>
        </div>
        <div class="col-6">
            <div class="card bg-light">
                <div class="card-body text-center">
                    <h5 class="sentiment-negative">負面詞數</h5>
                    <h2>${sentiment.negative_count}</h2>
                </div>
            </div>
        </div>
    </div>
    `;
    
    return html;
}

function loadSampleText() {
    fetch(`${API_BASE_URL}/input_texts/sample.txt`)
        .then(response => response.text())
        .then(text => {
            document.getElementById('analyzeText').value = text;
        })
        .catch(error => {
            console.error('Error loading sample text:', error);
            alert('無法載入範例文本');
        });
}

function convertText() {
    const text = document.getElementById('sourceText').value.trim();
    if (!text) {
        alert('請輸入要轉換的文本');
        return;
    }
    
    const direction = document.querySelector('input[name="conversionDirection"]:checked').value;
    
    fetch(`${API_BASE_URL}/api/convert`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            text: text,
            direction: direction
        }),
    })
    .then(response => response.json())
    .then(data => {
        if (data.error) {
            throw new Error(data.error);
        }
        document.getElementById('resultText').value = data.converted_text;
    })
    .catch(error => {
        console.error('Error:', error);
        alert('轉換失敗: ' + error.message);
    });
}

function copyResultText() {
    const resultText = document.getElementById('resultText');
    resultText.select();
    resultText.setSelectionRange(0, 99999); // For mobile devices
    
    navigator.clipboard.writeText(resultText.value)
        .then(() => {
            // Visual feedback that copy succeeded
            const copyBtn = document.getElementById('copyBtn');
            const originalText = copyBtn.innerHTML;
            
            copyBtn.innerHTML = '<i class="bi bi-check-lg"></i> 已複製';
            setTimeout(() => {
                copyBtn.innerHTML = originalText;
            }, 2000);
        })
        .catch(err => {
            console.error('Failed to copy text: ', err);
            alert('無法複製文本');
        });
}

function downloadConvertedText() {
    const text = document.getElementById('resultText').value;
    if (!text) {
        alert('沒有可下載的內容');
        return;
    }
    
    const direction = document.querySelector('input[name="conversionDirection"]:checked').value;
    const filename = direction === 'to_traditional' ? 'traditional_chinese.txt' : 'simplified_chinese.txt';
    
    const blob = new Blob([text], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    const a = document.createElement('a');
    a.href = url;
    a.download = filename;
    a.style.display = 'none';
    
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

function showImageInModal(src, alt) {
    const modal = new bootstrap.Modal(document.getElementById('imageModal'));
    const modalImage = document.getElementById('modalImage');
    const modalTitle = document.getElementById('imageModalLabel');
    const downloadBtn = document.getElementById('downloadModalImageBtn');
    
    modalImage.src = src;
    modalTitle.textContent = alt || '圖表預覽';
    
    // Set up download button
    downloadBtn.href = src;
    downloadBtn.download = alt ? alt.replace(/\s+/g, '_') + '.png' : 'visualization.png';
    
    modal.show();
}

function downloadImage(src, filename) {
    const a = document.createElement('a');
    a.href = src;
    a.download = filename;
    a.style.display = 'none';
    
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
    }, 100);
}

function generateReport() {
    if (!currentAnalysisResult || !currentAnalysisId) {
        return;
    }
    
    // Show loading indication in report tab
    document.getElementById('reportLoading').classList.remove('d-none');
    document.getElementById('reportContent').classList.add('d-none');
    
    // Select the report tab to show progress
    const reportTab = document.getElementById('report-tab');
    reportTab.click();
    
    // Update report stats
    const reportStatsList = document.getElementById('reportStats');
    reportStatsList.innerHTML = '';
    
    // Add basic stats
    const stats = [
        { name: '總詞數', value: currentAnalysisResult.total_words || 0 },
        { name: '平均詞長', value: currentAnalysisResult.avg_word_length || 0 },
        { name: '情感傾向', value: getSentimentLabel(currentAnalysisResult.sentiment?.sentiment_label) },
        { name: '正面詞數量', value: currentAnalysisResult.sentiment?.positive_count || 0 },
        { name: '負面詞數量', value: currentAnalysisResult.sentiment?.negative_count || 0 }
    ];
    
    stats.forEach(stat => {
        const li = document.createElement('li');
        li.className = 'list-group-item';
        li.innerHTML = `<strong>${stat.name}:</strong> ${stat.value}`;
        reportStatsList.appendChild(li);
    });
    
    // Check if interactive visualizations need to be generated
    if (!window.currentInteractiveResult) {
        // Generate interactive visualizations first, then generate the report
        generateInteractiveVisualizationsForReport();
        return;
    }
    
    // Gather all available data for comprehensive report
    let reportData = {
        analysis_data: { 
            ...currentAnalysisResult, 
            original_text: document.getElementById('analyzeText').value 
        },
        options: {
            basic: true,
            advanced: true,
            interactive: true,
            title: '中文文本分析完整報告',
            json: true,
            data: true,
            summary: true
        }
    };
    
    // Add similarity analysis data if available
    if (window.currentSimilarityResult) {
        reportData.similarity_data = window.currentSimilarityResult;
    }
    
    // Add interactive visualization data if available
    if (window.currentInteractiveResult) {
        reportData.interactive_data = window.currentInteractiveResult;
    }
    
    // Call the comprehensive report API
    fetch(`${API_BASE_URL}/api/generate_comprehensive_report`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify(reportData),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('報告生成失敗');
        }
        return response.json();
    })
    .then(data => {
        if (data.success) {
            // Update the current analysis ID to the new report ID
            const reportId = data.report_id;
    
    // Set up view report button
    const viewReportBtn = document.getElementById('viewReportBtn');
            viewReportBtn.href = `${API_BASE_URL}/static/results/${reportId}/report.html`;
    
    // Set up download report button
    const downloadReportBtn = document.getElementById('downloadReportBtn');
            downloadReportBtn.href = `${API_BASE_URL}/static/results/${reportId}/report.html`;
    downloadReportBtn.download = `chinese_text_analysis_report.html`;
    
    // Set up download all visualizations button
    const downloadAllBtn = document.getElementById('downloadAllVisualizationsBtn');
    downloadAllBtn.onclick = function() {
        downloadAllVisualizations();
    };
    
            // Update the complete report with interactive and similarity previews
            updateCompleteReportPreviews();
            
            // Hide loading and show content
            document.getElementById('reportLoading').classList.add('d-none');
            document.getElementById('reportContent').classList.remove('d-none');
        } else {
            throw new Error(data.error || '報告生成失敗');
        }
    })
    .catch(error => {
        console.error('Error generating report:', error);
        alert('報告生成失敗: ' + error.message);
        
        // Hide loading indication
        document.getElementById('reportLoading').classList.add('d-none');
        document.getElementById('reportContent').classList.remove('d-none');
    });
}

function getSentimentLabel(sentiment) {
    switch (sentiment) {
        case 'positive': return '正面';
        case 'negative': return '負面';
        case 'neutral': return '中性';
        default: return '未知';
    }
}

function downloadBasicVisualizations() {
    if (!currentAnalysisResult || !currentAnalysisResult.visualizations) {
        alert('無分析結果可下載');
        return;
    }
    
    // Basic visualizations include: wordcloud, word_frequency, pos_distribution, sentiment, entities
    const basicVizKeys = ['wordcloud', 'word_frequency', 'pos_distribution', 'sentiment', 'entities'];
    downloadSelectedVisualizations(basicVizKeys);
}

function downloadAdvancedVisualizations() {
    if (!currentAnalysisResult || !currentAnalysisResult.visualizations) {
        alert('無分析結果可下載');
        return;
    }
    
    // Advanced visualizations include: word_frequency_vertical, word_frequency_pie, keywords, ngrams, word_by_length
    const advancedVizKeys = [
        'word_frequency_vertical', 'word_frequency_pie', 'keywords', 'ngrams', 'word_by_length'
    ];
    downloadSelectedVisualizations(advancedVizKeys);
}

function downloadAllVisualizations() {
    // Collect all available visualizations from different sources
    let allVisualizations = {};
    
    // Add basic analysis visualizations
    if (currentAnalysisResult && currentAnalysisResult.visualizations) {
        Object.assign(allVisualizations, currentAnalysisResult.visualizations);
    }
    
    // Add interactive visualizations
    if (window.currentInteractiveResult && window.currentInteractiveResult.visualizations) {
        Object.assign(allVisualizations, window.currentInteractiveResult.visualizations);
    }
    
    // Add similarity analysis visualizations
    if (window.currentSimilarityResult && window.currentSimilarityResult.visualizations) {
        Object.assign(allVisualizations, window.currentSimilarityResult.visualizations);
    }
    
    // Filter out JSON results and get all keys
    const allVizKeys = Object.keys(allVisualizations)
        .filter(key => key !== 'results_json');
    
    if (allVizKeys.length === 0) {
        alert('無圖表可下載');
        return;
    }
    
    downloadSelectedVisualizationsFromMultipleSources(allVisualizations, allVizKeys);
}

function downloadSelectedVisualizationsFromMultipleSources(allVisualizations, keys) {
    ensureJSZip(() => {
        if (keys.length > 1) {
            const zip = new JSZip();
            let fetchCount = 0;
            const validKeys = keys.filter(k => allVisualizations[k]);
            
            validKeys.forEach(key => {
                if (allVisualizations[key]) {
                    fetch(allVisualizations[key])
                        .then(response => response.blob())
                        .then(blob => {
                            // Determine file extension based on the URL
                            const url = allVisualizations[key];
                            const extension = url.includes('.html') ? 'html' : 'png';
                            zip.file(`${key}.${extension}`, blob);
                            fetchCount++;
                            
                            if (fetchCount === validKeys.length) {
                                zip.generateAsync({ type: 'blob' })
                                    .then(content => {
                                        const url = URL.createObjectURL(content);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = 'chinese_text_analysis_all_visualizations.zip';
                                        a.style.display = 'none';
                                        document.body.appendChild(a);
                                        a.click();
                                        
                                        setTimeout(() => {
                                            document.body.removeChild(a);
                                            URL.revokeObjectURL(url);
                                        }, 100);
                                    });
                            }
                        })
                        .catch(error => {
                            console.error(`Error downloading ${key}:`, error);
                            fetchCount++; // Still increment to avoid hanging
                            
                            if (fetchCount === validKeys.length) {
                                zip.generateAsync({ type: 'blob' })
                                    .then(content => {
                                        const url = URL.createObjectURL(content);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = 'chinese_text_analysis_all_visualizations.zip';
                                        a.style.display = 'none';
                                        document.body.appendChild(a);
                                        a.click();
                                        
                                        setTimeout(() => {
                                            document.body.removeChild(a);
                                            URL.revokeObjectURL(url);
                                        }, 100);
                                    });
                            }
                        });
                }
            });
        } else if (keys.length === 1 && allVisualizations[keys[0]]) {
            const url = allVisualizations[keys[0]];
            const extension = url.includes('.html') ? 'html' : 'png';
            downloadImage(url, `${keys[0]}.${extension}`);
        }
    });
}

function downloadSelectedVisualizations(keys) {
    const visualizations = currentAnalysisResult.visualizations;
    
    // Create a zip file if more than one visualization
    if (keys.length > 1) {
        const zip = new JSZip();
        
        // Add all selected visualizations to the zip
        keys.forEach(key => {
            if (visualizations[key]) {
                // Create a fetch request for each image
                fetch(visualizations[key])
                    .then(response => response.blob())
                    .then(blob => {
                        // Add the blob to the zip file
                        zip.file(`${key}.png`, blob);
                        
                        // If all files are added, generate the zip
                        if (Object.keys(zip.files).length === keys.filter(k => visualizations[k]).length) {
                            zip.generateAsync({ type: 'blob' })
                                .then(content => {
                                    // Download the zip file
                                    const url = URL.createObjectURL(content);
                                    const a = document.createElement('a');
                                    a.href = url;
                                    a.download = 'chinese_text_analysis_visualizations.zip';
                                    a.style.display = 'none';
                                    document.body.appendChild(a);
                                    a.click();
                                    
                                    // Clean up
                                    setTimeout(() => {
                                        document.body.removeChild(a);
                                        URL.revokeObjectURL(url);
                                    }, 100);
                                });
                        }
                    });
            }
        });
    } else if (keys.length === 1 && visualizations[keys[0]]) {
        // Just download the single visualization
        downloadImage(visualizations[keys[0]], `${keys[0]}.png`);
    }
}

function downloadDataAsJson() {
    if (!currentAnalysisResult) {
        alert('無分析結果可下載');
        return;
    }
    
    // Create a JSON blob
    const json = JSON.stringify(currentAnalysisResult, null, 2);
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    
    // Download it
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chinese_text_analysis.json';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

function downloadDataAsCsv() {
    if (!currentAnalysisResult) {
        alert('無分析結果可下載');
        return;
    }
    
    // Create CSV content for word frequency
    let csv = '詞語,頻率\n';
    
    if (currentAnalysisResult.word_frequency) {
        // Sort by frequency (descending)
        const sortedItems = Object.entries(currentAnalysisResult.word_frequency)
            .sort((a, b) => b[1] - a[1]);
        
        sortedItems.forEach(([word, freq]) => {
            csv += `"${word}",${freq}\n`;
        });
    }
    
    // Create a CSV blob
    const blob = new Blob([csv], { type: 'text/csv;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    
    // Download it
    const a = document.createElement('a');
    a.href = url;
    a.download = 'chinese_text_word_frequency.csv';
    a.style.display = 'none';
    document.body.appendChild(a);
    a.click();
    
    // Clean up
    setTimeout(() => {
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
    }, 100);
}

function downloadEverything() {
    // Download all visualizations
    downloadAllVisualizations();
    
    // Download data as JSON
    downloadDataAsJson();
}

// External libraries needed for zip functionality
// We'll load JSZip dynamically only when needed
function ensureJSZip(callback) {
    if (window.JSZip) {
        callback();
        return;
    }
    
    const script = document.createElement('script');
    script.src = 'https://cdnjs.cloudflare.com/ajax/libs/jszip/3.10.1/jszip.min.js';
    script.onload = callback;
    document.head.appendChild(script);
}

// Call this before any operation that needs JSZip
function downloadSelectedVisualizations(keys) {
    ensureJSZip(() => {
        const visualizations = currentAnalysisResult.visualizations;
        
        if (keys.length > 1) {
            const zip = new JSZip();
            let fetchCount = 0;
            const validKeys = keys.filter(k => visualizations[k]);
            
            validKeys.forEach(key => {
                if (visualizations[key]) {
                    fetch(visualizations[key])
                        .then(response => response.blob())
                        .then(blob => {
                            zip.file(`${key}.png`, blob);
                            fetchCount++;
                            
                            if (fetchCount === validKeys.length) {
                                zip.generateAsync({ type: 'blob' })
                                    .then(content => {
                                        const url = URL.createObjectURL(content);
                                        const a = document.createElement('a');
                                        a.href = url;
                                        a.download = 'chinese_text_analysis_visualizations.zip';
                                        a.style.display = 'none';
                                        document.body.appendChild(a);
                                        a.click();
                                        
                                        setTimeout(() => {
                                            document.body.removeChild(a);
                                            URL.revokeObjectURL(url);
                                        }, 100);
                                    });
                            }
                        });
                }
            });
        } else if (keys.length === 1 && visualizations[keys[0]]) {
            downloadImage(visualizations[keys[0]], `${keys[0]}.png`);
        }
    });
}

// Advanced Features Functions

// Text Similarity Analysis
function analyzeSimilarity() {
    const textsInput = document.getElementById('similarityTexts').value.trim();
    if (!textsInput) {
        alert('請輸入要分析的文本');
        return;
    }
    
    // Split texts by lines and filter empty lines
    const texts = textsInput.split('\n').filter(text => text.trim().length > 0);
    
    if (texts.length < 2) {
        alert('至少需要輸入2個文本進行相似度分析');
        return;
    }
    
    // Show loading indicator
    document.getElementById('similarityLoadingIndicator').classList.remove('d-none');
    document.getElementById('noSimilarityResults').classList.add('d-none');
    document.getElementById('similarityResultsContent').classList.add('d-none');
    
    // Send request to similarity API
    fetch(`${API_BASE_URL}/api/similarity/analyze`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ texts: texts }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('相似度分析請求失敗');
        }
        return response.json();
    })
    .then(data => {
        displaySimilarityResults(data);
        // Automatically switch to similarity results tab
        const similarityTab = new bootstrap.Tab(document.getElementById('similarity-results-tab'));
        similarityTab.show();
    })
    .catch(error => {
        console.error('Error:', error);
        alert('相似度分析失敗: ' + error.message);
    })
    .finally(() => {
        document.getElementById('similarityLoadingIndicator').classList.add('d-none');
    });
}

function displaySimilarityResults(data) {
    // Store similarity results globally for report generation
    window.currentSimilarityResult = data;
    
    // Hide empty state and show results
    document.getElementById('noSimilarityResults').classList.add('d-none');
    document.getElementById('similarityResultsContent').classList.remove('d-none');
    
    // Update similarity visualizations
    if (data.visualizations) {
        updateVisualizationImage('similarityHeatmapImg', data.visualizations.similarity_heatmap);
        updateVisualizationImage('similarityNetworkImg', data.visualizations.similarity_network);
        
        // Update interactive visualizations
        if (data.visualizations.interactive_heatmap) {
            document.getElementById('openInteractiveHeatmapBtn').href = data.visualizations.interactive_heatmap;
            document.getElementById('openInteractiveHeatmapBtn').classList.remove('d-none');
            document.getElementById('interactiveHeatmapFrame').src = data.visualizations.interactive_heatmap;
            document.getElementById('interactiveHeatmapFrame').classList.remove('d-none');
            document.getElementById('heatmapPlaceholder').classList.add('d-none');
            document.getElementById('heatmapStatus').textContent = '已生成';
            document.getElementById('heatmapStatus').className = 'badge bg-success';
        }
        
        if (data.visualizations.interactive_network) {
            document.getElementById('openInteractiveNetworkBtn').href = data.visualizations.interactive_network;
            document.getElementById('openInteractiveNetworkBtn').classList.remove('d-none');
            document.getElementById('interactiveNetworkFrame').src = data.visualizations.interactive_network;
            document.getElementById('interactiveNetworkFrame').classList.remove('d-none');
            document.getElementById('networkPlaceholder').classList.add('d-none');
            document.getElementById('networkStatus').textContent = '已生成';
            document.getElementById('networkStatus').className = 'badge bg-success';
        }
        
        // Show interactive visualizations tab content
        document.getElementById('noInteractiveViz').classList.add('d-none');
        document.getElementById('interactiveVizContent').classList.remove('d-none');
        
        // Hide the visualization note if interactive visualizations are available
        if (data.visualizations.interactive_heatmap || data.visualizations.interactive_network) {
            if (document.getElementById('visualizationNote')) {
                document.getElementById('visualizationNote').classList.add('d-none');
            }
        }
    }
    
    // Display similarity matrix
    if (data.similarity_matrix) {
        displaySimilarityMatrix(data.similarity_matrix, data.labels);
    }
    
    // Update the complete report preview when similarity results are displayed
    updateCompleteReportPreviews();
}

function displaySimilarityMatrix(matrix, labels) {
    const container = document.getElementById('similarityMatrix');
    let html = '<table class="table table-bordered table-sm">';
    
    // Header row
    html += '<thead><tr><th></th>';
    labels.forEach(label => {
        html += `<th class="text-center" style="min-width: 100px;">${label.substring(0, 20)}...</th>`;
    });
    html += '</tr></thead><tbody>';
    
    // Data rows
    matrix.forEach((row, i) => {
        html += `<tr><td class="fw-bold">${labels[i].substring(0, 20)}...</td>`;
        row.forEach(similarity => {
            const color = similarity > 0.8 ? 'success' : similarity > 0.6 ? 'warning' : similarity > 0.4 ? 'info' : 'light';
            html += `<td class="text-center bg-${color} bg-opacity-25">${similarity.toFixed(3)}</td>`;
        });
        html += '</tr>';
    });
    
    html += '</tbody></table>';
    container.innerHTML = html;
}

function loadSimilarityExample() {
    const exampleTexts = [
        "今天天氣很好，陽光明媚，適合出門遊玩。",
        "今日天候良好，陽光普照，很適合外出活動。",
        "明天會下雨，記得帶雨傘出門。",
        "我喜歡閱讀，特別是科幻小說。"
    ];
    
    document.getElementById('similarityTexts').value = exampleTexts.join('\n');
}

// File Upload and Parsing
function uploadAndParseFile() {
    const fileInput = document.getElementById('fileInput');
    const file = fileInput.files[0];
    
    if (!file) {
        alert('請選擇一個文件');
        return;
    }
    
    // Show progress indicator
    document.getElementById('fileUploadProgress').classList.remove('d-none');
    document.getElementById('fileParseResult').classList.add('d-none');
    
    // Create form data
    const formData = new FormData();
    formData.append('file', file);
    
    // Send file to parsing API
    fetch(`${API_BASE_URL}/api/file/upload`, {
        method: 'POST',
        body: formData,
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('文件解析失敗');
        }
        return response.json();
    })
    .then(data => {
        displayFileParseResult(data);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('文件解析失敗: ' + error.message);
    })
    .finally(() => {
        document.getElementById('fileUploadProgress').classList.add('d-none');
    });
}

function displayFileParseResult(data) {
    // Show parse result
    document.getElementById('fileParseResult').classList.remove('d-none');
    
    // Display metadata
    const metadataContainer = document.getElementById('fileMetadata');
    let html = '<div class="row">';
    html += `<div class="col-md-6"><strong>文件名：</strong> ${data.filename}</div>`;
    html += `<div class="col-md-6"><strong>內容長度：</strong> ${data.content.length} 字符</div>`;
    
    if (data.metadata) {
        Object.entries(data.metadata).forEach(([key, value]) => {
            html += `<div class="col-md-6 mt-2"><strong>${key}：</strong> ${value}</div>`;
        });
    }
    
    html += '</div>';
    html += '<div class="mt-3"><strong>解析的內容預覽：</strong></div>';
    html += `<div class="border p-2 mt-2" style="max-height: 200px; overflow-y: auto; background-color: #f8f9fa;">
                ${data.content.substring(0, 500)}${data.content.length > 500 ? '...' : ''}
             </div>`;
    
    metadataContainer.innerHTML = html;
    
    // Store the parsed content for analysis
    window.parsedFileContent = data.content;
}

function analyzeFileContent() {
    if (!window.parsedFileContent) {
        alert('沒有解析的文件內容可以分析');
        return;
    }
    
    // Set the content to the main analysis textarea
    document.getElementById('analyzeText').value = window.parsedFileContent;
    
    // Switch to analyze tab
    const analyzeTab = new bootstrap.Tab(document.getElementById('analyze-tab'));
    analyzeTab.show();
    
    // Start analysis
    analyzeText();
}

// System Capabilities Check
function checkSystemCapabilities() {
    fetch(`${API_BASE_URL}/api/system/capabilities`)
    .then(response => response.json())
    .then(data => {
        let html = '<div class="alert alert-info"><h5>系統功能狀態</h5>';
        
        const features = [
            { key: 'similarity_analysis', name: '相似度分析' },
            { key: 'advanced_visualization', name: '高級視覺化' },
            { key: 'task_queue', name: '任務隊列' },
            { key: 'file_parsing', name: '文件解析' },
            { key: 'gpu_acceleration', name: 'GPU 加速' }
        ];
        
        features.forEach(feature => {
            const status = data[feature.key] ? '✅ 可用' : '❌ 不可用';
            html += `<div>${feature.name}: ${status}</div>`;
        });
        
        if (data.supported_formats) {
            html += `<div class="mt-2"><strong>支持的文件格式:</strong> ${data.supported_formats.join(', ')}</div>`;
        }
        
        html += '</div>';
        
        // Show in a modal or alert
        const tempDiv = document.createElement('div');
        tempDiv.innerHTML = html;
        document.body.appendChild(tempDiv);
        
        // You could replace this with a proper modal
        alert('系統功能檢查完成，請查看控制台或頁面上的詳細信息');
        
        setTimeout(() => {
            document.body.removeChild(tempDiv);
        }, 5000);
    })
    .catch(error => {
        console.error('Error:', error);
        alert('系統功能檢查失敗: ' + error.message);
    });
}

// Reset Interactive Visualizations
function resetInteractiveVisualizations() {
    // Reset heatmap
    document.getElementById('interactiveHeatmapFrame').src = '';
    document.getElementById('interactiveHeatmapFrame').classList.add('d-none');
    document.getElementById('heatmapPlaceholder').classList.remove('d-none');
    document.getElementById('openInteractiveHeatmapBtn').classList.add('d-none');
    document.getElementById('heatmapStatus').textContent = '等待生成';
    document.getElementById('heatmapStatus').className = 'badge bg-secondary';
    
    // Reset network
    document.getElementById('interactiveNetworkFrame').src = '';
    document.getElementById('interactiveNetworkFrame').classList.add('d-none');
    document.getElementById('networkPlaceholder').classList.remove('d-none');
    document.getElementById('openInteractiveNetworkBtn').classList.add('d-none');
    document.getElementById('networkStatus').textContent = '等待生成';
    document.getElementById('networkStatus').className = 'badge bg-secondary';
    
    // Show the visualization note
    if (document.getElementById('visualizationNote')) {
        document.getElementById('visualizationNote').classList.remove('d-none');
    }
}

// Generate Interactive Visualizations
function generateInteractiveVisualizations() {
    if (!currentAnalysisResult) {
        alert('請先進行文本分析');
        return;
    }
    
    // Send request to generate advanced visualizations
    fetch(`${API_BASE_URL}/api/visualizations/advanced`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ analysis_data: currentAnalysisResult }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('生成交互式圖表失敗');
        }
        return response.json();
    })
    .then(data => {
        displayInteractiveVisualizations(data.visualizations);
        // Don't switch to interactive tab - let user stay where they are
        // The complete report will be automatically updated with interactive visualizations
    })
    .catch(error => {
        console.error('Error:', error);
        alert('生成交互式圖表失敗: ' + error.message);
    });
}

// Generate Interactive Visualizations specifically for report generation
function generateInteractiveVisualizationsForReport() {
    if (!currentAnalysisResult) {
        alert('請先進行文本分析');
        return;
    }
    
    // Send request to generate advanced visualizations
    fetch(`${API_BASE_URL}/api/visualizations/advanced`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({ analysis_data: currentAnalysisResult }),
    })
    .then(response => {
        if (!response.ok) {
            throw new Error('生成交互式圖表失敗');
        }
        return response.json();
    })
    .then(data => {
        // Store the interactive visualization results
        displayInteractiveVisualizations(data.visualizations);
        
        // Now that interactive visualizations are ready, generate the report
        generateReport();
    })
    .catch(error => {
        console.error('Error:', error);
        
        // Even if interactive visualization generation fails, continue with the report
        // but without interactive visualizations
        generateReport();
    });
}

function displayInteractiveVisualizations(visualizations) {
    // Store interactive visualization results globally for report generation
    window.currentInteractiveResult = { visualizations: visualizations };
    
    // Hide empty state and show content
    document.getElementById('noInteractiveViz').classList.add('d-none');
    document.getElementById('interactiveVizContent').classList.remove('d-none');
    
    // Update treemap
    if (visualizations.treemap) {
        document.getElementById('openTreemapBtn').href = visualizations.treemap;
        document.getElementById('treemapFrame').src = visualizations.treemap;
    }
    
    // Update interactive word analysis
    if (visualizations.interactive_word_analysis) {
        // We can add this as another iframe if needed
    }
    
    // Update dashboard
    if (visualizations.dashboard) {
        document.getElementById('openDashboardBtn').href = visualizations.dashboard;
        document.getElementById('dashboardFrame').src = visualizations.dashboard;
    }
    
    // Update interactive heatmap (for single text analysis)
    if (visualizations.interactive_heatmap) {
        document.getElementById('openInteractiveHeatmapBtn').href = visualizations.interactive_heatmap;
        document.getElementById('openInteractiveHeatmapBtn').classList.remove('d-none');
        document.getElementById('interactiveHeatmapFrame').src = visualizations.interactive_heatmap;
        document.getElementById('interactiveHeatmapFrame').classList.remove('d-none');
        document.getElementById('heatmapPlaceholder').classList.add('d-none');
        document.getElementById('heatmapStatus').textContent = '已生成';
        document.getElementById('heatmapStatus').className = 'badge bg-success';
    }
    
    // Update interactive network (for single text analysis)
    if (visualizations.interactive_network) {
        document.getElementById('openInteractiveNetworkBtn').href = visualizations.interactive_network;
        document.getElementById('openInteractiveNetworkBtn').classList.remove('d-none');
        document.getElementById('interactiveNetworkFrame').src = visualizations.interactive_network;
        document.getElementById('interactiveNetworkFrame').classList.remove('d-none');
        document.getElementById('networkPlaceholder').classList.add('d-none');
        document.getElementById('networkStatus').textContent = '已生成';
        document.getElementById('networkStatus').className = 'badge bg-success';
    }
    
    // Hide the visualization note if interactive visualizations are available
    if (visualizations.interactive_heatmap || visualizations.interactive_network) {
        if (document.getElementById('visualizationNote')) {
            document.getElementById('visualizationNote').classList.add('d-none');
        }
    }
    
    // Update the complete report preview when interactive visualizations are generated
    updateCompleteReportPreviews();
}

// Function to update the complete report with interactive and similarity previews
function updateCompleteReportPreviews() {
    // Update interactive report preview in complete report
    updateInteractiveReportPreview();
    
    // Update similarity report preview in complete report  
    updateSimilarityReportPreview();
}

function updateInteractiveReportPreview() {
    const previewContainer = document.getElementById('interactiveReportThumbnails');
    const previewCard = document.getElementById('interactiveReportPreview');
    
    if (!previewContainer || !previewCard) return;
    
    // Check if interactive visualizations are available
    const hasInteractiveViz = document.getElementById('noInteractiveViz').classList.contains('d-none') && 
                             !document.getElementById('interactiveVizContent').classList.contains('d-none');
    
    if (hasInteractiveViz) {
        // Show the preview card
        previewCard.classList.remove('d-none');
        
        // Create thumbnails for interactive visualizations
        let html = '';
        const interactiveVizTypes = [
            { id: 'interactiveHeatmapFrame', name: '交互式熱力圖', icon: 'bi-grid-3x3' },
            { id: 'interactiveNetworkFrame', name: '交互式網絡圖', icon: 'bi-diagram-3' },
            { id: 'treemapFrame', name: '詞頻樹狀圖', icon: 'bi-tree' },
            { id: 'dashboardFrame', name: '綜合分析儀表板', icon: 'bi-speedometer2' }
        ];
        
        interactiveVizTypes.forEach(viz => {
            const frame = document.getElementById(viz.id);
            const isAvailable = frame && frame.src && !frame.classList.contains('d-none');
            const statusClass = isAvailable ? 'text-success' : 'text-muted';
            const statusIcon = isAvailable ? 'bi-check-circle-fill' : 'bi-circle';
            
            html += `
                <div class="col-md-6 mb-2">
                    <div class="d-flex align-items-center">
                        <i class="bi ${viz.icon} me-2 ${statusClass}"></i>
                        <span class="small ${statusClass}">${viz.name}</span>
                        <i class="bi ${statusIcon} ms-auto ${statusClass}"></i>
                    </div>
                </div>
            `;
        });
        
        previewContainer.innerHTML = html;
    } else {
        // Hide the preview card if no interactive visualizations
        previewCard.classList.add('d-none');
    }
}

function updateSimilarityReportPreview() {
    const previewContainer = document.getElementById('similarityReportThumbnails');
    const previewCard = document.getElementById('similarityReportPreview');
    
    if (!previewContainer || !previewCard) return;
    
    // Check if similarity results are available
    const hasSimilarityResults = document.getElementById('noSimilarityResults').classList.contains('d-none') && 
                                !document.getElementById('similarityResultsContent').classList.contains('d-none');
    
    if (hasSimilarityResults) {
        // Show the preview card
        previewCard.classList.remove('d-none');
        
        // Create thumbnails for similarity visualizations
        let html = '';
        const similarityVizTypes = [
            { id: 'similarityHeatmapImg', name: '相似度熱力圖', icon: 'bi-grid-3x3-gap' },
            { id: 'similarityNetworkImg', name: '相似度網絡圖', icon: 'bi-diagram-2' },
            { id: 'similarityMatrix', name: '相似度矩陣', icon: 'bi-table' }
        ];
        
        similarityVizTypes.forEach(viz => {
            const element = document.getElementById(viz.id);
            const isAvailable = element && ((element.tagName === 'IMG' && element.src) || 
                                          (element.tagName === 'DIV' && element.innerHTML.trim()));
            const statusClass = isAvailable ? 'text-success' : 'text-muted';
            const statusIcon = isAvailable ? 'bi-check-circle-fill' : 'bi-circle';
            
            html += `
                <div class="col-md-4 mb-2">
                    <div class="d-flex align-items-center">
                        <i class="bi ${viz.icon} me-2 ${statusClass}"></i>
                        <span class="small ${statusClass}">${viz.name}</span>
                        <i class="bi ${statusIcon} ms-auto ${statusClass}"></i>
                    </div>
                </div>
            `;
        });
        
        previewContainer.innerHTML = html;
    } else {
        // Hide the preview card if no similarity results
        previewCard.classList.add('d-none');
    }
}