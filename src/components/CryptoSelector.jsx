import React, { useState } from 'react';

const CryptoSelector = () => {
  const [activeCrypto, setActiveCrypto] = useState('bitcoin');

  const handleCryptoClick = (crypto) => {
    setActiveCrypto(crypto);
    // URL 변경도 함께 처리 (라우팅 사용 시)
    window.location.href = `/${crypto.toLowerCase()}`;
  };

  return (
    <div className="crypto-buttons">
      <button 
        className={activeCrypto === 'bitcoin' ? 'active' : ''}
        onClick={() => handleCryptoClick('bitcoin')}
      >
        Bitcoin
      </button>
      <button 
        className={activeCrypto === 'ethereum' ? 'active' : ''}
        onClick={() => handleCryptoClick('ethereum')}
      >
        Ethereum
      </button>
      <button 
        className={activeCrypto === 'ripple' ? 'active' : ''}
        onClick={() => handleCryptoClick('ripple')}
      >
        Ripple
      </button>
    </div>
  );
};

export default CryptoSelector; 