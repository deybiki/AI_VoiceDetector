// utils/mailTemplate.js

export function getEvaluationMailHTML({
   recipientName,
   testTitle,
   evaluationLink,
   additionalText = "",
   footerText = "If you have any questions, contact support.",
}) {
   return `
    <div style="font-family: Arial, sans-serif; max-width: 500px; margin: auto; border:1px solid #eee; border-radius:10px; padding: 24px;">
      <h2 style="color: #193a5e; margin-top: 0;">Hello ${recipientName},</h2>
      <p>
        ${additionalText ? additionalText : `The answers for your test <b>${testTitle}</b> are ready for evaluation.`}
      </p>
      <div style="margin: 24px 0;">
        <a href="${evaluationLink}" style="display:inline-block;padding:12px 24px;background:#193a5e;color:#fff;text-decoration:none;border-radius:6px;font-weight:bold;">
          Evaluate Answers
        </a>
      </div>
      <hr style="margin:24px 0;">
      <small style="color: #666;">${footerText}</small>
    </div>
  `;
}
