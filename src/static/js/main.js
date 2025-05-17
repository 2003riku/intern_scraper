/* インターン情報自動取得システム - メインJavaScript */

// グローバル変数
let allInternships = [];
let allCompanies = [];
let currentPage = 1;
const itemsPerPage = 10;
let filteredInternships = [];

// ページ読み込み時の処理
document.addEventListener('DOMContentLoaded', function() {
    // データの読み込み
    fetchData();
    
    // 検索とフィルタリングのイベントリスナー
    document.getElementById('searchInput').addEventListener('input', filterInternships);
    document.getElementById('industryFilter').addEventListener('change', filterInternships);
    document.getElementById('marketFilter').addEventListener('change', filterInternships);
    document.getElementById('resetFilters').addEventListener('click', resetFilters);
});

// データの取得
async function fetchData() {
    showLoading();
    
    try {
        // 企業データの取得
        const companiesResponse = await fetch('/api/companies');
        allCompanies = await companiesResponse.json();
        
        // インターンシップデータの取得
        const internshipsResponse = await fetch('/api/internships');
        allInternships = await internshipsResponse.json();
        
        // 業種フィルターの選択肢を生成
        populateIndustryFilter();
        
        // 初期表示
        filteredInternships = [...allInternships];
        renderInternships();
        
    } catch (error) {
        console.error('データの取得に失敗しました:', error);
        document.getElementById('internshipsTableBody').innerHTML = `
            <tr>
                <td colspan="6" class="text-center text-danger">
                    データの読み込みに失敗しました。ページを再読み込みしてください。
                </td>
            </tr>
        `;
    }
    
    hideLoading();
}

// 業種フィルターの選択肢を生成
function populateIndustryFilter() {
    const industryFilter = document.getElementById('industryFilter');
    const industries = new Set();
    
    // 企業データから業種を抽出
    allCompanies.forEach(company => {
        if (company.industry) {
            industries.add(company.industry);
        }
    });
    
    // 選択肢を追加
    industries.forEach(industry => {
        const option = document.createElement('option');
        option.value = industry;
        option.textContent = industry;
        industryFilter.appendChild(option);
    });
}

// インターンシップのフィルタリング
function filterInternships() {
    const searchTerm = document.getElementById('searchInput').value.toLowerCase();
    const selectedIndustry = document.getElementById('industryFilter').value;
    const selectedMarket = document.getElementById('marketFilter').value;
    
    // フィルタリング条件に基づいてインターンシップをフィルタリング
    filteredInternships = allInternships.filter(internship => {
        // 検索条件
        const matchesSearch = 
            internship.company_name.toLowerCase().includes(searchTerm) || 
            internship.title.toLowerCase().includes(searchTerm);
        
        // 業種条件
        let matchesIndustry = true;
        if (selectedIndustry) {
            const company = allCompanies.find(c => c.id === internship.company_id);
            matchesIndustry = company && company.industry === selectedIndustry;
        }
        
        // 市場区分条件
        let matchesMarket = true;
        if (selectedMarket) {
            const company = allCompanies.find(c => c.id === internship.company_id);
            matchesMarket = company && company.market === selectedMarket;
        }
        
        return matchesSearch && matchesIndustry && matchesMarket;
    });
    
    // 現在のページをリセットして再表示
    currentPage = 1;
    renderInternships();
}

// フィルターのリセット
function resetFilters() {
    document.getElementById('searchInput').value = '';
    document.getElementById('industryFilter').value = '';
    document.getElementById('marketFilter').value = '';
    
    filteredInternships = [...allInternships];
    currentPage = 1;
    renderInternships();
}

// インターンシップの表示
function renderInternships() {
    const tableBody = document.getElementById('internshipsTableBody');
    tableBody.innerHTML = '';
    
    // ページネーションの計算
    const startIndex = (currentPage - 1) * itemsPerPage;
    const endIndex = Math.min(startIndex + itemsPerPage, filteredInternships.length);
    const currentInternships = filteredInternships.slice(startIndex, endIndex);
    
    if (currentInternships.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="6" class="text-center">
                    条件に一致するインターンシップが見つかりませんでした。
                </td>
            </tr>
        `;
        document.getElementById('pagination').innerHTML = '';
        return;
    }
    
    // インターンシップの一覧を表示
    currentInternships.forEach(internship => {
        const row = document.createElement('tr');
        
        // 日付のフォーマット
        const startDate = internship.start_date ? formatDate(internship.start_date) : '未定';
        const endDate = internship.end_date ? formatDate(internship.end_date) : '未定';
        
        row.innerHTML = `
            <td>${internship.company_name}</td>
            <td>${internship.title}</td>
            <td>${startDate}</td>
            <td>${endDate}</td>
            <td>${internship.target || '記載なし'}</td>
            <td>
                <a href="${internship.application_url}" target="_blank" class="btn btn-sm btn-primary">
                    詳細を見る
                </a>
            </td>
        `;
        
        tableBody.appendChild(row);
    });
    
    // ページネーションの表示
    renderPagination();
}

// ページネーションの表示
function renderPagination() {
    const paginationElement = document.getElementById('pagination');
    const totalPages = Math.ceil(filteredInternships.length / itemsPerPage);
    
    if (totalPages <= 1) {
        paginationElement.innerHTML = '';
        return;
    }
    
    let paginationHTML = '<ul class="pagination">';
    
    // 前のページへのリンク
    paginationHTML += `
        <li class="page-item ${currentPage === 1 ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage - 1}" aria-label="Previous">
                <span aria-hidden="true">&laquo;</span>
            </a>
        </li>
    `;
    
    // ページ番号
    for (let i = 1; i <= totalPages; i++) {
        if (
            i === 1 || 
            i === totalPages || 
            (i >= currentPage - 2 && i <= currentPage + 2)
        ) {
            paginationHTML += `
                <li class="page-item ${i === currentPage ? 'active' : ''}">
                    <a class="page-link" href="#" data-page="${i}">${i}</a>
                </li>
            `;
        } else if (
            i === currentPage - 3 || 
            i === currentPage + 3
        ) {
            paginationHTML += `
                <li class="page-item disabled">
                    <a class="page-link" href="#">...</a>
                </li>
            `;
        }
    }
    
    // 次のページへのリンク
    paginationHTML += `
        <li class="page-item ${currentPage === totalPages ? 'disabled' : ''}">
            <a class="page-link" href="#" data-page="${currentPage + 1}" aria-label="Next">
                <span aria-hidden="true">&raquo;</span>
            </a>
        </li>
    `;
    
    paginationHTML += '</ul>';
    paginationElement.innerHTML = paginationHTML;
    
    // ページネーションのクリックイベント
    document.querySelectorAll('#pagination .page-link').forEach(link => {
        link.addEventListener('click', function(e) {
            e.preventDefault();
            const page = parseInt(this.dataset.page);
            if (page && page !== currentPage && page > 0 && page <= totalPages) {
                currentPage = page;
                renderInternships();
                // ページトップにスクロール
                window.scrollTo({
                    top: document.getElementById('internshipsTable').offsetTop - 100,
                    behavior: 'smooth'
                });
            }
        });
    });
}

// 日付のフォーマット
function formatDate(dateString) {
    if (!dateString) return '';
    
    const date = new Date(dateString);
    if (isNaN(date.getTime())) return dateString;
    
    return `${date.getFullYear()}年${date.getMonth() + 1}月${date.getDate()}日`;
}

// ローディング表示
function showLoading() {
    const tableBody = document.getElementById('internshipsTableBody');
    tableBody.innerHTML = `
        <tr>
            <td colspan="6">
                <div class="spinner-container">
                    <div class="spinner-border text-primary" role="status">
                        <span class="visually-hidden">Loading...</span>
                    </div>
                </div>
            </td>
        </tr>
    `;
    document.getElementById('pagination').innerHTML = '';
}

// ローディング非表示
function hideLoading() {
    // 特に何もしない（renderInternships内で上書きされる）
}
