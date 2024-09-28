document.getElementById('createFolderButton').addEventListener('click', function() {
    const folderName = prompt("請輸入資料夾名稱:");
    if (folderName) {
        fetch('/api/create_folder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ folder_name: folderName })
        })
        .then(response => response.json())
        .then(data => {
            alert(data.message || data.error);
            loadFolders();
        });
    }
});

document.getElementById('logoutButton').addEventListener('click', function() {
    window.location.href = '/logout';
});

function loadFolders() {
    fetch('/api/folders')
        .then(response => response.json())
        .then(data => {
            const folderList = document.getElementById('folderList');
            folderList.innerHTML = '';
            data.forEach(folder => {
                const li = document.createElement('li');
                li.textContent = folder;
                folderList.appendChild(li);
            });
        });
}

// 初始加载资料夹
loadFolders();
