interface SectionPageProps {
  description: string
  eyebrow: string
  title: string
}

export function SectionPage({ description, eyebrow, title }: SectionPageProps) {
  return (
    <section className="page-content">
      <span className="eyebrow">{eyebrow}</span>
      <h1>{title}</h1>
      <p className="page-intro">{description}</p>
      <div className="empty-state">
        <strong>基础路由已就绪</strong>
        <p>该页面将在对应业务功能开始实现时接入 API 和数据模型。</p>
      </div>
    </section>
  )
}
