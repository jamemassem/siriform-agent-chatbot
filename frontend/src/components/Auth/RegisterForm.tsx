import React, { useState } from 'react';
import { useAuth } from '../../contexts/AuthContext';
import styles from './AuthForms.module.css';

interface RegisterFormProps {
  onSuccess?: () => void;
  onSwitchToLogin?: () => void;
}

export const RegisterForm: React.FC<RegisterFormProps> = ({ onSuccess, onSwitchToLogin }) => {
  const { register } = useAuth();
  const [email, setEmail] = useState('');
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [fullName, setFullName] = useState('');
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setError('');

    // Validate password match
    if (password !== confirmPassword) {
      setError('รหัสผ่านไม่ตรงกัน');
      return;
    }

    // Validate password length
    if (password.length < 8) {
      setError('รหัสผ่านต้องมีอย่างน้อย 8 ตัวอักษร');
      return;
    }

    setIsLoading(true);

    try {
      await register(email, username, password, fullName || undefined);
      if (onSuccess) onSuccess();
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Registration failed');
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className={styles.authForm}>
      <h2 className={styles.title}>สมัครสมาชิก</h2>
      <form onSubmit={handleSubmit}>
        <div className={styles.formGroup}>
          <label htmlFor="email">อีเมล *</label>
          <input
            type="email"
            id="email"
            value={email}
            onChange={(e) => setEmail(e.target.value)}
            required
            disabled={isLoading}
            placeholder="example@email.com"
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="username">ชื่อผู้ใช้ *</label>
          <input
            type="text"
            id="username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
            disabled={isLoading}
            placeholder="ชื่อผู้ใช้ (3-50 ตัวอักษร)"
            minLength={3}
            maxLength={50}
            pattern="[a-zA-Z0-9_-]+"
            title="ใช้ได้เฉพาะตัวอักษร ตัวเลข ขีดกลาง และขีดล่าง"
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="fullName">ชื่อ-นามสกุล</label>
          <input
            type="text"
            id="fullName"
            value={fullName}
            onChange={(e) => setFullName(e.target.value)}
            disabled={isLoading}
            placeholder="ชื่อ นามสกุล (ไม่จำเป็น)"
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="password">รหัสผ่าน *</label>
          <input
            type="password"
            id="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
            disabled={isLoading}
            placeholder="รหัสผ่านอย่างน้อย 8 ตัวอักษร"
            minLength={8}
          />
        </div>

        <div className={styles.formGroup}>
          <label htmlFor="confirmPassword">ยืนยันรหัสผ่าน *</label>
          <input
            type="password"
            id="confirmPassword"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
            disabled={isLoading}
            placeholder="กรอกรหัสผ่านอีกครั้ง"
            minLength={8}
          />
        </div>

        {error && <div className={styles.error}>{error}</div>}

        <button type="submit" className={styles.submitButton} disabled={isLoading}>
          {isLoading ? 'กำลังสมัครสมาชิก...' : 'สมัครสมาชิก'}
        </button>

        {onSwitchToLogin && (
          <p className={styles.switchText}>
            มีบัญชีอยู่แล้ว?{' '}
            <button
              type="button"
              className={styles.switchButton}
              onClick={onSwitchToLogin}
              disabled={isLoading}
            >
              เข้าสู่ระบบ
            </button>
          </p>
        )}
      </form>
    </div>
  );
};
